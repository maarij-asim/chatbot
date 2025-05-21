import streamlit as st
import openai
import os
import requests
from io import BytesIO

# Set up OpenAI API key
if "OPENAI_API_KEY" not in os.environ:
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = 
else:
    api_key = os.environ["OPENAI_API_KEY"]

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

def generate_image(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("Chatbot with OpenAI (Text & Image)")
st.write("Type 'generate image <description>' to create an image. Type 'quit' to clear the chat.")

# Initialize session state for chat history and images
if "messages" not in st.session_state:
    st.session_state.messages = []
if "images" not in st.session_state:
    st.session_state.images = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display generated images
for image_url in st.session_state.images:
    st.image(image_url, caption="Generated Image", use_column_width=False, width=300)

# Input field for user message
user_input = st.chat_input("Ask anything or type 'generate image <description>':")

if user_input:
    if user_input.lower() == "quit":
        st.session_state.messages = []
        st.session_state.images = []
        st.experimental_rerun()
    elif not api_key:
        st.error("Please enter your OpenAI API key to continue.")
    else:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Check if user wants to generate an image
        if user_input.lower().startswith("generate image"):
            prompt = user_input[13:].strip()  # Extract prompt after "generate image"
            if not prompt:
                response = "Please provide a description for the image."
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)
            else:
                with st.spinner("Generating image..."):
                    image_url = generate_image(prompt)
                    if image_url.startswith("Error"):
                        st.session_state.messages.append({"role": "assistant", "content": image_url})
                        with st.chat_message("assistant"):
                            st.markdown(image_url)
                    else:
                        st.session_state.images.append(image_url)
                        st.session_state.messages.append({"role": "assistant", "content": f"Generated image for: {prompt}"})
                        with st.chat_message("assistant"):
                            st.markdown(f"Generated image for: {prompt}")
                        st.experimental_rerun()  # Refresh to show image
        else:
            # Handle regular chat response
            response = get_chatbot_response(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
