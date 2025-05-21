import streamlit as st
import openai
import os

# Set up OpenAI API key
# Note: In VS Code, store your API key in a .env file or environment variable for security
if "OPENAI_API_KEY" not in os.environ:
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
else:
    api_key = os.environ["OPENAI_API_KEY"]

# Initialize OpenAI client
client = openai.OpenAI()

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

# Streamlit UI
st.title("Chatbot with OpenAI")
st.write("Enter your message below. Type 'quit' to clear the chat.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input field for user message
user_input = st.chat_input("Ask anything:")

if user_input:
    if user_input.lower() == "quit":
        st.session_state.messages = []
        st.experimental_rerun()
    else:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get and display bot response
        if api_key:
            response = get_chatbot_response(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
        else:
            st.error("Please enter your OpenAI API key to continue.")
