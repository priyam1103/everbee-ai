from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os
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
from langchain_community.chat_message_histories import RedisChatMessageHistory
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

app = FastAPI()

origins = ["*"]

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

chat = ChatOpenAI(model="gpt-3.5-turbo-1106")
db = SQLDatabase.from_uri("postgresql://postgres:Everbee1o123@everbee-stag.ctimiq1vdoms.us-west-1.rds.amazonaws.com:5432/test_migration")

class UserInput(BaseModel):
    input: str

class SessionIdInput(BaseModel):
    input: str

@app.post("/chat/")
def chat_with_agent(user_input: UserInput, session_id: SessionIdInput):
    config = {"configurable": {"session_id": f"{session_id.input}"}}
    response = conversational_agent_executor.invoke(
                    {
                        "input": f"{user_input.input}",
                    },
                    config=config
                )
    return {"response": response['output']}

@tool
def db_ll_agent(user_input):
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

tools = [keyword_trend, db_ll_agent, search_youtube, generate_image, search_google]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Hello how are you?""",
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
    lambda session_id: RedisChatMessageHistory(
        session_id, url=f"{os.environ.get('REDIS_URL')}"
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
