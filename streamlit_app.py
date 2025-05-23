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
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="Chatbot by Maarij",
    page_icon="🤖",
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
    
    .new-chat-btn {
        background-color: #2f2f2f !important;
        color: white !important;
        border: 1px solid #565869 !important;
        width: 100% !important;
        margin-bottom: 1rem !important;
    }
    
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
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# JavaScript for Text-to-Speech
def speak_text(text):
    js_code = f"""
    <script>
        function speakText() {{
            var utterance = new SpeechSynthesisUtterance("{text}");
            utterance.lang = 'en-US';
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }}
        speakText();
    </script>
    """
    components.html(js_code, height=0)

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
    if "tts_enabled" not in st.session_state:
        st.session_state.tts_enabled = True  # Default TTS enabled

# Load API key from environment or session
def load_api_key():
    if "OPENAI_API_KEY" in os.environ:
        st.session_state.api_key = os.environ["OPENAI_API_KEY"]
        st.session_state.api_key_set = True
    elif st.session_state.api_key:
        st.session_state.api_key_set = True

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
            {"role": "system", "content": "You are a helpful, knowledgeable, and friendly AI assistant. Provide clear, accurate, and engaging responses."}
        ]
        
        # Add conversation history (last 10 messages to stay within token limits)
        recent_messages = messages[-10:] if len(messages) > 10 else messages
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
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <span class="message-avatar assistant-avatar">AI</span>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
            # Speak the assistant's response if TTS is enabled
            if st.session_state.tts_enabled:
                # Escape quotes in the message content to avoid JavaScript errors
                safe_content = message["content"].replace('"', '\\"').replace('\n', ' ')
                speak_text(safe_content)

# Main app
def main():
    init_session_state()
    load_api_key()
    
    # Sidebar
    with st.sidebar:
        st.title("💬 ChatGPT Assistant")
        
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
            "Model",
            ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
            help="Choose the AI model"
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
        
        # Text-to-Speech Toggle
        st.session_state.tts_enabled = st.checkbox(
            "Enable Text-to-Speech",
            value=st.session_state.tts_enabled,
            help="Toggle to enable/disable reading assistant responses aloud"
        )
        
        # Clear Current Chat
        if st.button("🗑️ Clear Current Chat", help="Clear current conversation"):
            st.session_state.messages = []
            st.rerun()

    # Main content area
    st.title("🤖 Assistant")
    st.markdown("*made by maarij-asim*")
    
    # API Key Status
    if not st.session_state.api_key_set:
        st.error("⚠️ Please set your OpenAI API key in the sidebar to start chatting")
        return
    
    # Welcome message for new chats
    if not st.session_state.messages:
        st.markdown("""
        ### Welcome! 👋
        
        I'm your AI assistant, ready to help with:
        - **Questions & Explanations** - Ask me anything you'd like to understand
        - **Creative Writing** - Stories, poems, scripts, and more
        - **Code Help** - Programming assistance, debugging, and explanations  
        - **Analysis & Research** - Break down complex topics
        - **Brainstorming** - Generate ideas and solutions
        
        **Example prompts to get started:**
        """)
        
        # Example buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💡 Explain quantum computing simply"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Explain quantum computing in simple terms"
                })
                st.rerun()
            
            if st.button("💻 Help debug JavaScript code"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Help me debug this JavaScript code"
                })
                st.rerun()
        
        with col2:
            if st.button("✍️ Write a creative short story"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Write a creative short story about time travel"
                })
                st.rerun()
            
            if st.button("🍽️ Plan a healthy meal"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Plan a healthy meal for the week"
                })
                st.rerun()
    
    # Display chat messages
    if st.session_state.messages:
        display_messages()
    
    # Chat input
    st.markdown("---")
    
    # Create columns for input and button
    input_col, button_col = st.columns([4, 1])
    
    with input_col:
        user_input = st.text_area(
            "Message",
            placeholder="Type your message here... (Press Ctrl+Enter to send)",
            height=100,
            label_visibility="collapsed"
        )
    
    with button_col:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        send_button = st.button("➤ Send", type="primary", use_container_width=True)
    
    # Handle message sending
    if send_button and user_input.strip():
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
        
        # Get AI response
        with st.spinner("🤔 Thinking..."):
            try:
                # Create a synchronous wrapper for the async function
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
    **Tips:**
    - Use /clear to clear current chat
    - Use /new to start a new chat
    - Press Ctrl+Enter in the text area to send quickly
    - Use the sidebar to manage your chat history
    - Toggle Text-to-Speech in the sidebar
    """)

if __name__ == "__main__":
    main()


### Explanation of Changes
1. **Web Speech API**:
   - Added a `speak_text` function that uses the Web Speech API (`SpeechSynthesisUtterance`) to convert text to speech in the browser.
   - The JavaScript code is injected using `streamlit.components.v1.html` with a height of 0 to avoid visual clutter.
   - The `lang`, `rate`, and `pitch` properties are set for a clear, natural-sounding voice (English US, default speed, and pitch).

2. **Text-to-Speech Trigger**:
   - In the `display_messages` function, after rendering an assistant message, the response content is passed to `speak_text` if TTS is enabled.
   - The message content is escaped (replacing quotes and newlines) to prevent JavaScript errors.

3. **TTS Toggle**:
   - Added a checkbox in the sidebar (`Enable Text-to-Speech`) to allow users to enable/disable TTS.
   - Stored in `st.session_state.tts_enabled`, defaulting to `True`.

4. **Dependencies**:
   - Added `import streamlit.components.v1 as components` to support JavaScript injection.
   - No additional Python packages are required since the Web Speech API is browser-based.

