from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional
import os
import re
import redis
import json
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.tools import YouTubeSearchTool
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_community.tools.google_trends import GoogleTrendsQueryRun
from langchain_community.utilities.google_trends import GoogleTrendsAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_message_histories import (
    PostgresChatMessageHistory,
)
from elasticsearch import Elasticsearch
import psycopg2
from decimal import Decimal
from json import JSONEncoder

app = FastAPI()

origins = ["*"]

class DateTimeEncoder(JSONEncoder):
    """Custom encoder for datetime and Decimal types for JSON serialization."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)  # or str(obj) if you want to avoid potential floating-point issues
        return JSONEncoder.default(self, obj)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],      
    allow_headers=["*"], 
)

os.environ["OPENAI_API_KEY"] = os.environ.get('OPENAI_API_KEY')
# Uncomment the below to use LangSmith. Not required.
os.environ["LANGCHAIN_API_KEY"] = os.environ.get('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["SERPAPI_API_KEY"] = os.environ.get('SERPAPI_API_KEY')
os.environ["GOOGLE_CSE_ID"] = os.environ.get('GOOGLE_CSE_ID')
os.environ["GOOGLE_API_KEY"] = os.environ.get('GOOGLE_API_KEY')

redis_s = redis.Redis.from_url(os.environ.get('REDIS_URL'), decode_responses=True)

chat = ChatOpenAI(model="gpt-3.5-turbo-1106")
db = SQLDatabase.from_uri(os.environ.get('DB_URI'))

class UserInput(BaseModel):
    input: str

class SessionIdInput(BaseModel):
    input: str

class UserEmailInput(BaseModel):
    input: str

@app.post("/chat/")
def chat_with_agent(user_input: UserInput, session_id: SessionIdInput):
    config = {"configurable": {"session_id": f"{session_id.input}"}}
    email = extract_last_segment(session_id.input)
    user_info = cached_fetch_user_details(email)
    print(user_info)
    response = conversational_agent_executor.invoke(
                    {
                        "input": f"{user_input.input}",
                        "email": f"{email}",
                        "user_info": f"{user_info}"
                    },
                    config=config
                )
    
    conn = psycopg2.connect(os.environ.get('DB_URI'))
    cur = conn.cursor()

    query = """
        SELECT *
        FROM message_store
        WHERE session_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """
    cur.execute(query, (session_id.input,))

    records = cur.fetchall()
    cur.close()
    conn.close()

    # Convert records to a list of dicts
    columns = [desc[0] for desc in cur.description]
    thread = [dict(zip(columns, record)) for record in records]

    return {"response": response['output'], "created_at": thread[0]["created_at"], "thread_info": thread[0]}

@app.get("/user/threads")
def get_all_threads(user_email: str = Query(..., description="User email")):
    conn = psycopg2.connect(os.environ.get('DB_URI'))
    cur = conn.cursor()

    query = """
    SELECT DISTINCT ON (session_id) *
    FROM message_store
    WHERE session_id LIKE '%{}%'
    ORDER BY session_id, created_at DESC
    """.format(user_email)

    cur.execute(query)
    records = cur.fetchall()
    cur.close()
    conn.close()

    columns = [desc[0] for desc in cur.description]
    response = [dict(zip(columns, record)) for record in records]

    return {"response": response}

@app.get("/user/thread")
def get_single_thread_chat(session_id: str = Query(..., description="The session ID to fetch chat messages for")):
    conn = psycopg2.connect(os.environ.get('DB_URI'))
    cur = conn.cursor()

    query = """
    SELECT *
    FROM message_store
    WHERE session_id = %s
    ORDER BY created_at ASC
    """
    cur.execute(query, (session_id,))

    records = cur.fetchall()
    cur.close()
    conn.close()

    # Convert records to a list of dicts
    columns = [desc[0] for desc in cur.description]
    response = [dict(zip(columns, record)) for record in records]

    return {"response": response}

def cached_fetch_user_details(email):
    # Try to get the cached data
    cached_user = redis_s.get(email)
    if cached_user:
        print("Fetching from cache")
        return json.loads(cached_user)

    # If not cached, fetch the data from the primary source
    print("Fetching from the database")
    user_info = fetch_user_details(email)  # Replace with your actual function to fetch data

    # Cache the data for future use, set expiration as needed
    redis_s.set(email, json.dumps(user_info, cls=DateTimeEncoder), ex=3600)  # Cache for 1 hour; adjust as needed

    user_info_p = f"""Activate Buzz AI with the following user and shop-specific details to provide tailored e-commerce assistance for Etsy shop optimization and growth. Buzz AI is designed to empower Etsy shop owners with personalized, data-driven advice, enhancing their shop performance and user engagement on the Etsy platform.
                    **User and Shop-Specific Details:**
                    {user_info}
                    **Capabilities and Interaction Guidelines:**
                    1. Use the shop-specific details to provide insights on sales trends, product performance, and optimization opportunities.
                    2. Advise on listing enhancements, marketing strategies, and customer engagement tactics based on current e-commerce and Etsy-specific trends.
                    3. Maintain an approachable, supportive tone, offering clear and concise advice to ensure recommendations are actionable and effective.
                    4. Adapt responses to user queries, employing the detailed shop information to offer personalized guidance and solutions.
                    **Tone and Engagement:**
                    - Buzz AI should be friendly and encouraging, fostering a positive interaction environment.
                    - Advice should be delivered in a straightforward manner, avoiding unnecessary complexity or jargon.
                    - Responses should be tailored to the user's specific situation, with a focus on actionable insights and strategies.
                    **Upon Receiving a Query, Buzz AI Will:**
                    1. Assess the query in the context of the provided shop-specific details and the user's unique needs.
                    2. Deliver customized advice and insights aimed at addressing the query, leveraging the detailed shop information for precision.
                    3. Encourage further dialogue and provide additional clarification as needed, ensuring the user feels fully supported and informed.
                    This comprehensive prompt equips Buzz AI to act as a valuable resource for Etsy shop owners, combining in-depth shop analysis with expert e-commerce advice to drive shop growth and enhance user engagement."""
    return user_info_p

def fetch_user_details(email):
    # Assuming you have a function to get user details from a database
    # This is a placeholder for the actual implementation
    conn = psycopg2.connect(os.environ.get('DB_URI'))
    cur = conn.cursor()
    print(email)
    query = """
        SELECT *
        FROM users
        WHERE email = %s
    """
    cur.execute(query, (email,))

    records = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    query1 = """
        SELECT
            u.email AS "UserEmail",
            STRING_AGG(s.shop_name, ', ') AS "ShopNames",
            SUM(s.transaction_sold_count) AS "AnnualSales",
            SUM(s.listing_active_count) AS "ListingsCount",
            SUM(s.revenue) AS "AnnualRevenue",
            AVG(s.review_average) AS "AverageReviewScore",
            AVG(s.shop_age_month) AS "UserAge"
        FROM
            users u
        JOIN
            sales_channels sc ON u.id = sc.user_id
        JOIN
            shops s ON sc.shop_id = s.id
        WHERE
            u.email = %s
        GROUP BY
            u.email;
    """
    cur.execute(query1, (email,))

    records1 = cur.fetchall()
    columns1 = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()
    

    # Convert records to a list of dicts
    if records:
        # Convert records to a list of dictionaries
        users = [dict(zip(columns, record)) for record in records]
        shops = [dict(zip(columns1, record)) for record in records1]
        # Return the first user's information
        return {"user_info": users[0], "shop_info": shops[0]}
    else:
        # Handle the case where no records are found
        print("No user found")
        return {"user_info": None}

def extract_last_segment(s):
    # Split the string by hyphen
    parts = s.split('-')
    
    # Return the last element of the list
    return parts[-1]

@tool
def db_ll_agent(user_input, email: str):
    """The SQL Query Agent is designed to interact with a SQL database to answer user queries. It generates syntactically correct SQL queries in a specific dialect and executes them to retrieve relevant information. The agent is constrained to select queries and is programmed to ensure efficient and secure access to the database.
       user has_many sales_channels and sales_channels has_one shop and shop has_many listings"""

    agent = create_sql_agent(
        llm=chat,
        db=db,
        verbose=True,
        agent_type="openai-tools",
    )
    print("agent created")
    qq = f"""System: You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the given tools. Only use the information returned by the tools to construct your final answer.

    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    If the question does not seem related to the database, just return "I don't know" as the answer.

    ALWAYS keep in mind -
        user has_many sales_channels and sales_channels has_one shops and shops has_many listings
        user is not directly connected to listings
        shop is not directly connected to user
        To get shop details  user has_many sales_channels and sales_channels has_one shops and shops has_many listings

    Here are some examples of user inputs and their corresponding SQL queries:

    User input: Find a user.
    SQL query: SELECT * FROM users WHERE email='priyam@everbee.io';
      
    User input: Information about shop/know more about my shop
    SQL query: SELECT
            u.id AS user_id,
            u.name AS user_name,
            u.email AS user_email,
            sc.id AS sales_channel_id,
            sc.name AS sales_channel_name,
            s.id AS shop_id,
            s.name AS shop_name,
        FROM
            users u WHERE email='priyam@everbee.io'
        JOIN
            sales_channels sc ON u.id = sc.user_id
        JOIN
            shops s ON sc.id = s.sales_channel_id;
                    

    User input: Category that a user sells.
    SQL query: SELECT DISTINCT l.main_category, DISTINCT l.sub_category
            FROM users u
            JOIN sales_channels sc ON u.id = sc.user_id
            JOIN shops s ON sc.id = s.sales_channel_id
            JOIN listings l ON s.id = l.shop_id
            WHERE u.email = priyam@everbee.io;
                    
    User input: can you suggest me some listings to sell depending upon my shop
    SQL query: WITH user_categories AS (
            SELECT DISTINCT l.main_category
            FROM users u
            JOIN sales_channels sc ON u.id = sc.user_id
            JOIN shops s ON sc.id = s.sales_channel_id
            JOIN listings l ON s.id = l.shop_id
            WHERE u.email = priyam@everbee.io
            )
            SELECT l.*
            FROM listings l
            JOIN user_categories uc ON l.main_category = uc.main_category
            WHERE l.cached_listing_age_in_months < 6
            AND l.cached_est_mo_sales > 20
            ORDER BY l.main_category, l.cached_est_mo_sales DESC;    

    User input: can you suggest me some best/trending listings to sell 
    SQL query: SELECT l.*
            FROM listings l
            WHERE l.cached_listing_age_in_months < 6
            AND l.cached_est_mo_sales > 20
            ORDER BY l.cached_est_mo_sales DESC;       

    User Email: {email}
    Human: {user_input}"""
    print(qq)
    out = agent.invoke(qq)

    return out['output']

@tool
def keyword_trend(keyword: str) -> dict:
    """Get Google Trends for a given keyword."""
    tool = GoogleTrendsQueryRun(api_wrapper=GoogleTrendsAPIWrapper())
    return tool.run(keyword)

@tool
def generate_image(image_prompt: str) -> dict:
    """Generate image/design for a given prompt"""
    prompt = PromptTemplate(
        input_variables=["image_desc"],
        template="Generate a detailed prompt to generate an image based on the following description: {image_desc}",
    )
    chain = LLMChain(llm=chat, prompt=prompt)
    image_url = DallEAPIWrapper().run(chain.run(image_prompt))
    return image_url

@tool
def search_youtube(keyword: str):
    """search_youtube searches YouTube videos, it can find tutorials, videos, guides , anything from youtube
        YouTube is a free video sharing website that makes it easy to watch online videos. You can even create and upload your own videos to share with others."""
    tool = YouTubeSearchTool()
    return tool.run(keyword)

@tool
def search_google(keyword: str):
    """search_google searches the web for any information, it can you tell anything that no one knows
        Google Search is a search engine operated by Google. It allows users to search for information on the Internet by entering keywords or phrases. Google Search uses algorithms to analyze and rank websites based on their relevance to the search query. It is the most popular search engine worldwide."""
    search = GoogleSearchAPIWrapper()
    tool = Tool(
        name="google_search",
        description="Search Google for recent results.",
        func=search.run,
    )
    return tool.run(keyword)

@tool
def website_retriever(site_url: str, input: str):
    """Use this tool to access a external websites link
        capability to access specific details from any other external websites"""
    loader = WebBaseLoader(site_url)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_documents(data)
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever(k=4)
    docs = retriever.invoke(input)
    print(docs)
    return docs

def load_mappings(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
@tool
def get_listings_data(input: str):
    """Use this tool to effortlessly give information about listings. """

    mappinngs = load_mappings('mappings.json')

    mappings_string = json.dumps(mappinngs, indent=4)

    client = Elasticsearch(
        os.environ.get('ES_URL'),
        basic_auth=(os.environ.get('ES_USERNAME'), os.environ.get('ES_PASS'))
    )

    template = f"""Given the mapping delimited by triple backticks ```{mappings_string}``` translate the text delimited by triple quotes in a valid Elasticsearch DSL query '''{input}''' Give me only the json code part of the answer. Compress the json output removing spaces."""
    print(template)
    query_terms = chat.invoke(template)
    generated_query = query_terms.content

    es_query = generated_query
    print(es_query)

    response = client.search(
        index="listings_development",
        body=es_query
    )
    res=[]
    for hit in response['hits']['hits']:
        print(hit['_score'], hit['_source']['title'], hit['_source']['cached_est_mo_revenue'])
        res.append(hit['_source']['title'])

    return res

tools = [keyword_trend, search_youtube, generate_image, search_google, website_retriever, get_listings_data]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            {user_info}""",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_openai_tools_agent(chat, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


conversational_agent_executor = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: PostgresChatMessageHistory(
        session_id=session_id, connection_string=os.environ.get('DB_URI'),
    ),
    input_messages_key="input",
    output_messages_key="output",
    history_messages_key="chat_history",
)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


# export LANGCHAIN_TRACING_V2=true
# export LANGCHAIN_API_KEY="ls__1507118dac01425c9825e04be325dff0"
# export LANGCHAIN_PROJECT="everbee-ai-stag"
# export OPENAI_API_KEY="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"
