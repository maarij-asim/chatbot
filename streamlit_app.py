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
# st.title("Chatbot with OpenAI")
# st.write("Enter your message below. Type 'quit' to clear the chat.")

# # Initialize session state for chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat history
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Input field for user message
# user_input = st.chat_input("Ask anything:")

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
#             st.error("Please enter your OpenAI API key to continue.")

import streamlit as st
import openai
import os
import requests
from io import BytesIO
from datetime import datetime
import pytz

# Load OpenAI API key from Streamlit secrets
try:
    OPENAI_API_KEY = st.secrets["OpenAI_key"]
except KeyError:
    st.error("OpenAI API key not found in Streamlit secrets. Please add 'OpenAI_key' to your secrets.")
    st.stop()
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Optional: Check for a whitelist (if you want to restrict access)
# Replace "sally" with actual usernames you want to allow
if "whitelist" in st.secrets:
    allowed_users = st.secrets["whitelist"]
    # Placeholder for user authentication (e.g., via Streamlit's st.text_input for username)
    # For simplicity, this is not fully implemented; add if needed
    # Example: username = st.text_input("Enter your username")
    # if username not in allowed_users:
    #     st.error("Access denied. Your username is not in the whitelist.")
    #     st.stop()
else:
    allowed_users = None  # No whitelist; open access

# Initialize OpenAI client
try:
    client = openai.OpenAI()
except Exception as e:
    st.error(f"Failed to initialize OpenAI client: {str(e)}")
    st.stop()

def get_chatbot_response(messages, model="gpt-4o", max_tokens=300):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def generate_image(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI configuration
st.set_page_config(page_title="Professional AI Chatbot", layout="wide")
st.markdown("""
    <style>
        .main {background-color: #f5f5f5;}
        .stChatMessage {border-radius: 10px; padding: 10px; margin: 5px;}
        .user-message {background-color: #d1e7ff; color: #333;}
        .assistant-message {background-color: #ffffff; color: #333; border: 1px solid #ddd;}
        .stTextInput > div > input {border-radius: 20px;}
        .stButton > button {border-radius: 20px; background-color: #007bff; color: white;}
        .timestamp {font-size: 0.8em; color: #888;}
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🤖 Professional AI Chatbot")
st.markdown("Chat with AI or generate images by typing 'generate image <description>'. Type 'quit' to clear the conversation.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a professional, friendly, and highly knowledgeable AI assistant, similar to ChatGPT."}]
if "images" not in st.session_state:
    st.session_state.images = []

# Display chat history
for msg in st.session_state.messages[1:]:  # Skip system message
    role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(role, avatar="🧑" if role == "user" else "🤖"):
        st.markdown(f"<div class='{role}-message'>{msg['content']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='timestamp'>{msg.get('timestamp', '')}</div>", unsafe_allow_html=True)

# Display generated images
for idx, image_url in enumerate(st.session_state.images):
    st.image(image_url, caption=f"Generated Image {idx + 1}", use_column_width=False, width=300)

# Input field
user_input = st.chat_input("Type your message or 'generate image <description>'...")

if user_input:
    # Add timestamp (Pakistan Time Zone)
    pkt = pytz.timezone("Asia/Karachi")
    timestamp = datetime.now(pkt).strftime("%I:%M %p, %b %d, %Y")

    if user_input.lower() == "quit":
        st.session_state.messages = [{"role": "system", "content": "You are a professional, friendly, and highly knowledgeable AI assistant, similar to ChatGPT."}]
        st.session_state.images = []
        st.experimental_rerun()
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='timestamp'>{timestamp}</div>", unsafe_allow_html=True)

        # Handle image generation
        if user_input.lower().startswith("generate image"):
            prompt = user_input[13:].strip()
            if not prompt:
                response = "Please provide a description for the image."
                st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='timestamp'>{timestamp}</div>", unsafe_allow_html=True)
            else:
                with st.spinner("Generating image..."):
                    image_url = generate_image(prompt)
                    if image_url.startswith("Error"):
                        st.session_state.messages.append({"role": "assistant", "content": image_url, "timestamp": timestamp})
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(f"<div class='assistant-message'>{image_url}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='timestamp'>{timestamp}</div>", unsafe_allow_html=True)
                    else:
                        st.session_state.images.append(image_url)
                        response = f"Generated image for: {prompt}"
                        st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='timestamp'>{timestamp}</div>", unsafe_allow_html=True)
                        st.experimental_rerun()
        else:
            # Handle text response with conversation history
            with st.spinner("Thinking..."):
                response = get_chatbot_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='timestamp'>{timestamp}</div>", unsafe_allow_html=True)

