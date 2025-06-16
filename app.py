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
#             st.error("Please enter your OpenAI API key to continue.")


import streamlit as st
import openai
import os
import json
import time
from datetime import datetime
import uuid
import re
import requests
from PIL import Image
from io import BytesIO

# Page configuration
st.set_page_config(
    page_icon="https://instagram.fkhi2-2.fna.fbcdn.net/v/t1.15752-9/491219689_977675274440582_5502547115889655741_n.jpg?stp=dst-jpg_s480x480_tt6&_nc_cat=108&ccb=1-7&_nc_sid=0024fc&_nc_ohc=NTWrSfIab8sQ7kNvwEor_AE&_nc_oc=Adk7IC74HY10qHcwqzoVScSXi9WpTvK9cGz05b92PP1bL2GdjIuOzxx2mrAvPySFEUs&_nc_zt=23&_nc_ht=instagram.fkhi2-2.fna&oh=03_Q7cD2QHvad8pZ9oYgX-UWkshsquk6q3o9NoPaXQ0BjZd63QZMg&oe=685E556A",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-like styling
st.markdown("""
<style>
    /* Main app styling */
    .main > div {
        padding: 1rem 2rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #171717;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #2f2f2f;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #5436da;
    }
    
    .assistant-message {
        background-color: #343541;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #10a37f;
    }
    
    .image-message {
        background-color: #343541;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #ff6b6b;
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
    }
    
    .user-avatar {
        background-color: #5436da;
        color: white;
    }
    
    .assistant-avatar {
        background-color: #10a37f;
        color: white;
    }
    
    .image-avatar {
        background-color: #ff6b6b;
        color: white;
    }
    
    /* Input styling */
    .stTextArea textarea {
        background-color: #40414f;
        color: white;
        border: 1px solid #565869;
        border-radius: 12px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #10a37f;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #0d8a6b;
    }
    
    /* Image button styling */
    .image-button > button {
        background-color: #ff6b6b !important;
        color: white !important;
    }
    
    .image-button > button:hover {
        background-color: #ff5252 !important;
    }
    
    /* Sidebar button styling */
    .new-chat-btn {
        background-color: #2f2f2f !important;
        color: white !important;
        border: 1px solid #565869 !important;
        width: 100% !important;
        margin-bottom: 1rem !important;
    }
    
    /* Success/Error messages */
    .success-message {
        background-color: #10a37f;
        color: white;
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    .error-message {
        background-color: #d73a49;
        color: white;
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    /* Image styling */
    .generated-image {
        max-width: 100%;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = False

# Load API key from environment or session
def load_api_key():
    if "OPENAI_API_KEY" in os.environ:
        st.session_state.api_key = os.environ["OPENAI_API_KEY"]
        st.session_state.api_key_set = True
    elif st.session_state.api_key:
        st.session_state.api_key_set = True

# Check if message is requesting image generation
def is_image_request(message):
    image_keywords = [
        "generate image", "create image", "make image", "draw", "paint", "sketch",
        "generate picture", "create picture", "make picture", "visualize",
        "show me", "picture of", "image of", "photo of", "illustration of",
        "dall-e", "dalle", "generate art", "create art", "make art"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in image_keywords)

# Extract image prompt from message
def extract_image_prompt(message):
    # Remove common prefixes
    prefixes_to_remove = [
        "generate image of", "create image of", "make image of", "draw",
        "generate picture of", "create picture of", "make picture of",
        "show me", "picture of", "image of", "photo of", "illustration of",
        "generate", "create", "make", "paint", "sketch", "visualize"
    ]
    
    prompt = message.lower()
    for prefix in prefixes_to_remove:
        if prompt.startswith(prefix):
            prompt = prompt[len(prefix):].strip()
            break
    
    # If prompt is still the same, try to extract after keywords
    if prompt == message.lower():
        for keyword in ["of ", "a ", "an "]:
            if keyword in prompt:
                prompt = prompt.split(keyword, 1)[1]
                break
    
    return prompt if prompt != message.lower() else message

# Generate image using DALL-E
async def generate_image(prompt, size="1024x1024", quality="standard", style="vivid"):
    try:
        client = openai.OpenAI(api_key=st.session_state.api_key)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=1,
        )
        
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        
        return {
            "success": True,
            "image_url": image_url,
            "revised_prompt": revised_prompt
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Download and display image
def download_and_display_image(image_url):
    try:
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None

# Save chat to history
def save_chat():
    if st.session_state.current_chat_id and st.session_state.messages:
        chat_title = generate_chat_title()
        st.session_state.chat_history[st.session_state.current_chat_id] = {
            "title": chat_title,
            "messages": st.session_state.messages.copy(),
            "timestamp": datetime.now().isoformat()
        }

# Generate chat title from first message
def generate_chat_title():
    if st.session_state.messages:
        first_message = st.session_state.messages[0]["content"]
        title = first_message[:50] + "..." if len(first_message) > 50 else first_message
        return title
    return "New Chat"

# Create new chat
def new_chat():
    save_chat()  # Save current chat before creating new one
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.messages = []

# Load existing chat
def load_chat(chat_id):
    save_chat()  # Save current chat before switching
    if chat_id in st.session_state.chat_history:
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = st.session_state.chat_history[chat_id]["messages"].copy()
    else:
        st.session_state.messages = []

# Delete chat
def delete_chat(chat_id):
    if chat_id in st.session_state.chat_history:
        del st.session_state.chat_history[chat_id]
        if st.session_state.current_chat_id == chat_id:
            new_chat()

# Get chatbot response
async def get_chatbot_response(messages, model="gpt-4o-mini", max_tokens=1000):
    try:
        client = openai.OpenAI(api_key=st.session_state.api_key)
        
        # Prepare messages for OpenAI API
        api_messages = [
            {"role": "system", "content": "You are a helpful, knowledgeable, and friendly AI assistant. Provide clear, accurate, and engaging responses. If someone asks you to generate, create, or make an image, let them know that you can help them with image generation using DALL-E, but they should use specific image generation commands or buttons in the interface."}
        ]
        
        # Add conversation history (last 10 messages to stay within token limits)
        # Filter out image messages for API call
        text_messages = [msg for msg in messages if msg.get("type") != "image"]
        recent_messages = text_messages[-10:] if len(text_messages) > 10 else text_messages
        
        for msg in recent_messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
        
        response = client.chat.completions.create(
            model=model,
            messages=api_messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Display chat messages
def display_messages():
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <span class="message-avatar user-avatar">You</span>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        elif message.get("type") == "image":
            st.markdown(f"""
            <div class="image-message">
                <span class="message-avatar image-avatar">🎨</span>
                <strong>Generated Image:</strong> {message.get("prompt", "Image")}
            </div>
            """, unsafe_allow_html=True)
            
            # Display the image
            if message.get("image_url"):
                image = download_and_display_image(message["image_url"])
                if image:
                    st.image(image, caption=f"Generated: {message.get('revised_prompt', message.get('prompt', ''))}", use_container_width=True)
            
            # Show revised prompt if available
            if message.get("revised_prompt") and message.get("revised_prompt") != message.get("prompt"):
                st.markdown(f"*DALL-E revised prompt: {message['revised_prompt']}*")
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <span class="message-avatar assistant-avatar">AI</span>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

# Main app
def main():
    init_session_state()
    load_api_key()
    
    # Sidebar
    with st.sidebar:
        st.title("💬 AI Assistant")
        
        # New Chat Button
        if st.button("➕ New Chat", key="new_chat", help="Start a new conversation"):
            new_chat()
            st.rerun()
        
        st.markdown("---")
        
        # Chat History
        st.subheader("Chat History")
        
        if st.session_state.chat_history:
            # Sort chats by timestamp (most recent first)
            sorted_chats = sorted(
                st.session_state.chat_history.items(), 
                key=lambda x: x[1]["timestamp"], 
                reverse=True
            )
            
            for chat_id, chat_data in sorted_chats:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if st.button(
                        chat_data["title"], 
                        key=f"load_{chat_id}",
                        help="Load this conversation"
                    ):
                        load_chat(chat_id)
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"delete_{chat_id}", help="Delete this chat"):
                        delete_chat(chat_id)
                        st.rerun()
        else:
            st.info("No chat history yet. Start a conversation!")
        
        st.markdown("---")
        
        # Settings
        st.subheader("⚙️ Settings")
        
        # API Key Management
        if not st.session_state.api_key_set:
            st.warning("Please set your OpenAI API key")
            api_key_input = st.text_input(
                "OpenAI API Key", 
                type="password", 
                placeholder="sk-...",
                help="Enter your OpenAI API key"
            )
            
            if st.button("Set API Key"):
                if api_key_input and api_key_input.startswith("sk-"):
                    st.session_state.api_key = api_key_input
                    st.session_state.api_key_set = True
                    st.success("API key set successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Please enter a valid OpenAI API key")
        else:
            st.success("✅ API key is set")
            if st.button("Change API Key"):
                st.session_state.api_key = ""
                st.session_state.api_key_set = False
                st.rerun()
        
        # Model Selection
        model_option = st.selectbox(
            "Chat Model",
            ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
            help="Choose the AI model for text responses"
        )
        
        # Image Generation Settings
        st.subheader("🎨 Image Settings")
        
        image_size = st.selectbox(
            "Image Size",
            ["1024x1024", "1792x1024", "1024x1792"],
            help="Size of generated images"
        )
        
        image_quality = st.selectbox(
            "Image Quality",
            ["standard", "hd"],
            help="Quality of generated images"
        )
        
        image_style = st.selectbox(
            "Image Style",
            ["vivid", "natural"],
            help="Style of generated images"
        )
        
        # Max Tokens
        max_tokens = st.slider(
            "Max Tokens",
            min_value=50,
            max_value=2000,
            value=1000,
            step=50,
            help="Maximum response length"
        )
        
        # Clear Current Chat
        if st.button("🗑️ Clear Current Chat", help="Clear current conversation"):
            st.session_state.messages = []
            st.rerun()

    # Main content area
    st.title("AI Assistant with Image Generation")
    st.markdown("*Made by Maarij Zeeshan*")
    
    # API Key Status
    if not st.session_state.api_key_set:
        st.error("⚠️ Please set your OpenAI API key in the sidebar to start chatting")
        return
    
    # Welcome message for new chats
    if not st.session_state.messages:
        st.markdown("""
        ### Welcome! 👋
        
        I'm your AI assistant with both **text** and **image generation** capabilities! I can help with:
        
        **💬 Text Conversations:**
        - Questions & Explanations
        - Creative Writing
        - Code Help & Programming
        - Analysis & Research
        - Brainstorming
        
        **🎨 Image Generation:**
        - Create artwork and illustrations
        - Generate concept art
        - Design logos and graphics
        - Visualize ideas and concepts
        
        **Example prompts to get started:**
        """)
        
        # Example buttons
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💬 Text Examples:**")
            if st.button("💡 Explain quantum computing"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Explain quantum computing in simple terms"
                })
                st.rerun()
            
            if st.button("💻 Help debug code"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Help me debug this JavaScript code"
                })
                st.rerun()
        
        with col2:
            st.markdown("**🎨 Image Examples:**")
            if st.button("🌅 Generate sunset landscape", key="img1"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Generate image of a beautiful sunset over mountains"
                })
                st.rerun()
            
            if st.button("🚀 Create futuristic city", key="img2"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Create image of a futuristic cyberpunk city"
                })
                st.rerun()
    
    # Display chat messages
    if st.session_state.messages:
        display_messages()
    
    # Chat input
    st.markdown("---")
    
    # Create columns for input and buttons
    input_col, text_button_col, image_button_col = st.columns([3, 1, 1])
    
    with input_col:
        user_input = st.text_area(
            "Message",
            placeholder="Type your message here... Use 'generate image of...' for image creation",
            height=100,
            label_visibility="collapsed"
        )
    
    with text_button_col:
        st.markdown("<br>", unsafe_allow_html=True)
        send_button = st.button("💬 Send Text", type="primary", use_container_width=True)
    
    with image_button_col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="image-button">', unsafe_allow_html=True)
        image_button = st.button("🎨 Generate Image", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle message sending
    if (send_button or image_button) and user_input.strip():
        if not st.session_state.current_chat_id:
            st.session_state.current_chat_id = str(uuid.uuid4())
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show user message
        st.markdown(f"""
        <div class="user-message">
            <span class="message-avatar user-avatar">You</span>
            {user_input}
        </div>
        """, unsafe_allow_html=True)
        
        if image_button or is_image_request(user_input):
            # Generate image
            image_prompt = extract_image_prompt(user_input)
            
            with st.spinner("🎨 Generating image..."):
                try:
                    import asyncio
                    
                    # Get or create event loop
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # Generate image
                    result = loop.run_until_complete(
                        generate_image(image_prompt, image_size, image_quality, image_style)
                    )
                    
                    if result["success"]:
                        # Add image message
                        st.session_state.messages.append({
                            "role": "assistant",
                            "type": "image",
                            "content": f"Generated image: {image_prompt}",
                            "prompt": image_prompt,
                            "revised_prompt": result["revised_prompt"],
                            "image_url": result["image_url"]
                        })
                        
                        st.success("🎨 Image generated successfully!")
                    else:
                        st.error(f"❌ Error generating image: {result['error']}")
                        
                        # Add error message
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"I encountered an error while generating the image: {result['error']}. Please try again with a different prompt."
                        })
                    
                    # Save chat
                    save_chat()
                    
                    # Rerun to show the new message
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            # Get text response
            with st.spinner("🤔 Thinking..."):
                try:
                    import asyncio
                    
                    # Get or create event loop
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # Run the async function
                    response = loop.run_until_complete(
                        get_chatbot_response(st.session_state.messages, model_option, max_tokens)
                    )
                    
                    # Add AI response
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Save chat
                    save_chat()
                    
                    # Rerun to show the new message
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error getting response: {str(e)}")
    
    # Handle special commands
    if user_input.lower().strip() == "/clear":
        st.session_state.messages = []
        st.rerun()
    elif user_input.lower().strip() == "/new":
        new_chat()
        st.rerun()
    
    # Instructions at bottom
    st.markdown("---")
    st.markdown("""
    **💡 Tips:**
    - **Text Chat**: Use the "💬 Send Text" button for regular conversations
    - **Image Generation**: Use the "🎨 Generate Image" button or include phrases like "generate image of...", "create picture of...", etc.
    - **Commands**: Use `/clear` to clear current chat, `/new` to start a new chat
    - **Quick Send**: Press Ctrl+Enter in the text area
    - **History**: Use the sidebar to manage your chat history
    
    **🎨 Image Generation Examples:**
    - "Generate image of a sunset over the ocean"
    - "Create a futuristic robot"
    - "Draw a cute cartoon cat"
    - "Make a logo for a coffee shop"
    """)

if __name__ == "__main__":
    main()
