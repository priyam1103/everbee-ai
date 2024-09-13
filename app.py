import streamlit as st

# Set up app title and layout
st.title("Simple Chat App")
st.write("Welcome to the simple chat app!")

# Initialize session state to store the chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Function to display chat messages
def display_chat():
    for message in st.session_state["messages"]:
        st.text_area(message["sender"], value=message["text"], height=50, max_chars=None, key=message["id"], disabled=True)

# Form to enter new messages
with st.form(key="chat_form"):
    user_message = st.text_input("Your Message", key="user_input")
    submit_button = st.form_submit_button(label="Send")

# Add user's message to the chat history if submitted
if submit_button and user_message:
    st.session_state["messages"].append({"sender": "You", "text": user_message, "id": len(st.session_state["messages"])})
    st.session_state["messages"].append({"sender": "Bot", "text": f"Echo: {user_message}", "id": len(st.session_state["messages"])+1})

# Display chat history
display_chat()
