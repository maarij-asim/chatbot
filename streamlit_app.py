# import streamlit as st
# import openai
# import os

# # Set up OpenAI API key
# # Note: In VS Code, store your API key in a .env file or environment variable for security
# if "OPENAI_API_KEY" not in os.environ:
#     api_key = st.text_input("Enter your OpenAI API key:", type="password")
#     if api_key:
#         os.environ["OPENAI_API_KEY"] = api_key
# else:
#     api_key = os.environ["OPENAI_API_KEY"]

# # Initialize OpenAI client
# client = openai.OpenAI()

# def get_chatbot_response(user_input, model="gpt-4o-mini", max_tokens=150):
#     try:
#         response = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {"role": "system", "content": "You are a helpful and friendly chatbot."},
#                 {"role": "user", "content": user_input}
#             ],
#             max_tokens=max_tokens,
#             temperature=0.7
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"Error: {str(e)}"

# # Streamlit UI
# st.title("Chatbot by maarij-asim")
# st.write("Hey there how can I assist you today")

# # Initialize session state for chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat history
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Input field for user message
# user_input = st.chat_input("Ask anything")

# if user_input:
#     if user_input.lower() == "quit":
#         st.session_state.messages = []
#         st.experimental_rerun()
#     else:
#         # Add user message to history
#         st.session_state.messages.append({"role": "user", "content": user_input})
#         with st.chat_message("user"):
#             st.markdown(user_input)

#         # Get and display bot response
#         if api_key:
#             response = get_chatbot_response(user_input)
#             st.session_state.messages.append({"role": "assistant", "content": response})
#             with st.chat_message("assistant"):
#                 st.markdown(response)
#         else:
#             st.error("Please enter your OpenAI API key to continue.

# Chatbot App with Professional ChatGPT-style UI
import streamlit as st
import openai
import os
import json
import time
from datetime import datetime
import uuid
import asyncio

# Page configuration
st.set_page_config(
    page_title="Chatbot by Maarij",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main > div { padding: 1rem 2rem; }
    .css-1d391kg { background-color: #171717; }
    .user-message, .assistant-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #2f2f2f;
        border-left: 4px solid #5436da;
    }
    .assistant-message {
        background-color: #343541;
        border-left: 4px solid #10a37f;
    }
    .message-avatar {
        display: inline-block;
        width: 32px;
        height: 32px;
        border-radius: 4px;
        text-align: center;
        line-height: 32px;
        font-weight: bold;
        font-size: 14px;
        margin-right: 12px;
        color: white;
    }
    .user-avatar { background-color: #5436da; }
    .assistant-avatar { background-color: #10a37f; }
    .stTextArea textarea {
        background-color: #40414f;
        color: white;
        border: 1px solid #565869;
        border-radius: 12px;
    }
    .stButton > button {
        background-color: #10a37f;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover { background-color: #0d8a6b; }
    .new-chat-btn { background-color: #2f2f2f !important; color: white !important; border: 1px solid #565869 !important; width: 100%; margin-bottom: 1rem; }
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
def init_session():
    for key, default in {
        "messages": [],
        "chat_history": {},
        "current_chat_id": None,
        "api_key": "",
        "api_key_set": False
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

# --- API Key Loader ---
def load_api_key():
    if "OPENAI_API_KEY" in os.environ:
        st.session_state.api_key = os.environ["OPENAI_API_KEY"]
        st.session_state.api_key_set = True
    elif st.session_state.api_key:
        st.session_state.api_key_set = True

# --- Save Current Chat ---
def save_chat():
    if st.session_state.current_chat_id and st.session_state.messages:
        st.session_state.chat_history[st.session_state.current_chat_id] = {
            "title": generate_title(),
            "messages": st.session_state.messages.copy(),
            "timestamp": datetime.now().isoformat()
        }

# --- Generate Title ---
def generate_title():
    if st.session_state.messages:
        first_msg = st.session_state.messages[0]["content"]
        return first_msg[:50] + "..." if len(first_msg) > 50 else first_msg
    return "New Chat"

# --- New Chat ---
def new_chat():
    save_chat()
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.messages = []

# --- Load Chat ---
def load_chat(chat_id):
    save_chat()
    chat = st.session_state.chat_history.get(chat_id, {})
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = chat.get("messages", []).copy()

# --- Delete Chat ---
def delete_chat(chat_id):
    st.session_state.chat_history.pop(chat_id, None)
    if st.session_state.current_chat_id == chat_id:
        new_chat()

# --- Chat Completion Function ---
def get_response(messages, model="gpt-4o-mini", max_tokens=1000):
    try:
        openai.api_key = st.session_state.api_key
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful assistant."}] + messages[-10:],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- Display Messages ---
def display_messages():
    for msg in st.session_state.messages:
        role_class = "user-message" if msg["role"] == "user" else "assistant-message"
        avatar_class = "user-avatar" if msg["role"] == "user" else "assistant-avatar"
        label = "You" if msg["role"] == "user" else "AI"
        st.markdown(f"""
        <div class="{role_class}">
            <span class="message-avatar {avatar_class}">{label}</span>
            {msg['content']}
        </div>
        """, unsafe_allow_html=True)

# --- Main Application ---
def main():
    init_session()
    load_api_key()

    with st.sidebar:
        st.title("💬 Chat Assistant")
        if st.button("➕ New Chat", key="new_chat_btn"):
            new_chat()
            st.rerun()

        st.subheader("Chat History")
        for chat_id, chat in sorted(st.session_state.chat_history.items(), key=lambda x: x[1]["timestamp"], reverse=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(chat["title"], key=f"load_{chat_id}"):
                    load_chat(chat_id)
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{chat_id}"):
                    delete_chat(chat_id)
                    st.rerun()

        st.subheader("Settings")
        if not st.session_state.api_key_set:
            api_input = st.text_input("OpenAI API Key", type="password")
            if st.button("Set API Key"):
                if api_input.startswith("sk-"):
                    st.session_state.api_key = api_input
                    st.session_state.api_key_set = True
                    st.success("API key set.")
                    st.rerun()
                else:
                    st.error("Invalid API key.")
        else:
            st.success("API key set.")
            if st.button("Change API Key"):
                st.session_state.api_key = ""
                st.session_state.api_key_set = False
                st.rerun()

        model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"])
        max_tokens = st.slider("Max Tokens", 50, 2000, 1000, 50)
        if st.button("Clear Current Chat"):
            st.session_state.messages = []
            st.rerun()

    st.title("🤖 Assistant")
    if not st.session_state.api_key_set:
        st.warning("Please enter your OpenAI API key in the sidebar.")
        return

    if not st.session_state.messages:
        st.markdown("""
        ### Welcome! 👋
        Ask me anything. Examples:
        - Explain quantum computing simply
        - Write a creative story
        - Help debug Python code
        """)

    display_messages()

    input_col, button_col = st.columns([4, 1])
    with input_col:
        user_input = st.text_area("", placeholder="Type a message...", height=100, label_visibility="collapsed")
    with button_col:
        st.markdown("<br>", unsafe_allow_html=True)
        send = st.button("Send")

    if send and user_input.strip():
        if not st.session_state.current_chat_id:
            st.session_state.current_chat_id = str(uuid.uuid4())

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            reply = get_response(st.session_state.messages, model=model, max_tokens=max_tokens)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            save_chat()
            st.rerun()

if __name__ == "__main__":
    main()

