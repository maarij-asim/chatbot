import streamlit as st
import openai
import os
from datetime import datetime
import pytz

# Load OpenAI API key from Streamlit secrets
try:
    OPENAI_API_KEY = st.secrets["OpenAI_key"]
except KeyError:
    st.error("OpenAI API key not found in Streamlit secrets. Please add 'OpenAI_key' to your secrets.")
    st.stop()
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Initialize OpenAI client
try:
    client = openai.OpenAI()
except Exception as e:
    st.error(f"Failed to initialize OpenAI client: {str(e)}")
    st.stop()

def get_chatbot_response(user_input, model="gpt-4o-mini", max_tokens=150):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful and friendly chatbot."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI configuration
st.set_page_config(page_title="Professional Chatbot", layout="wide")
st.markdown("""
    <style>
        .main {background-color: #f5f5f5;}
        .stChatMessage {border-radius: 10px; padding: 10px; margin: 5px;}
        .user-message {background-color: #d1e7ff; color: #333;}
        .assistant-message {background-color: #ffffff; color: #333; border: 1px solid #ddd;}
        .stTextInput > div > input {border-radius: 20px;}
        .timestamp {font-size: 0.8em; color: #888;}
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🤖 Professional Chatbot with OpenAI")
st.markdown("Enter your message below. Type 'quit' to clear the chat.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role, avatar="🧑" if role == "user" else "🤖"):
        st.markdown(f"<div class='{role}-message'>{message['content']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='timestamp'>{message.get('timestamp', '')}</div>", unsafe_allow_html=True)

# Input field for user message
user_input = st.chat_input("Ask anything:")

if user_input:
    # Add timestamp (Pakistan Time Zone)
    pkt = pytz.timezone("Asia/Karachi")
    timestamp = datetime.now(pkt).strftime("%I:%M %p, %b %d, %Y")

    if user_input.lower() == "quit":
        st.session_state.messages = []
        st.experimental_rerun()
    else:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='timestamp'>{timestamp}</div>", unsafe_allow_html=True)

        # Get and display bot response
        with st.spinner("Thinking..."):
            response = get_chatbot_response(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='timestamp'>{timestamp}</div>", unsafe_allow_html=True)
