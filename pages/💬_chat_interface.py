import streamlit as st
import requests
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="Chat Interface", layout="wide", page_icon="💬")

# Get backend URL from environment
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }

.stApp { background: #f4f6f9; }

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.header-container {
    background: linear-gradient(135deg, #1a2332 0%, #243447 100%);
    padding: 1.2rem 2rem;
    box-shadow: 0 4px 20px rgba(26,35,50,0.2);
    border-radius: 0;
    margin: -3.5rem -5rem 5rem -5rem;
}

.header-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #f5f0e8;
    margin: 0;
}

.stChatMessage {
    background: transparent !important;
}

.stChatMessage[data-testid="chat-message-user"] {
    flex-direction: row-reverse;
}

.stChatMessage[data-testid="chat-message-user"] > div {
    background: #1a2332 !important;
    color: #f5f0e8 !important;
    border-radius: 18px 18px 4px 18px !important;
    margin-left: 20% !important;
}

.stChatMessage[data-testid="chat-message-assistant"] > div {
    background: #ffffff !important;
    color: #1a2332 !important;
    border: 1px solid #dde3ea !important;
    border-radius: 18px 18px 18px 4px !important;
    margin-right: 20% !important;
    box-shadow: 0 1px 3px rgba(26,35,50,0.1) !important;
}

.stChatInputContainer {
    background: #ffffff !important;
    border: 1px solid #dde3ea !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(26,35,50,0.06) !important;
}

.stChatInputContainer textarea {
    border: none !important;
    background: transparent !important;
    font-size: 0.95rem !important;
    color: #1a2332 !important;
}

.stChatInputContainer textarea::placeholder {
    color: #8a9bb0 !important;
}

.welcome-msg {
    text-align: center;
    padding: 1.7rem 2rem;
    color: #6b7c93;
}

.welcome-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.7;
}

.welcome-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a2332;
    margin-bottom: 0.5rem;
}

.welcome-subtitle {
    font-size: 1rem;
    margin-bottom: 2rem;
}

.sidebar-title {
    background: #1a2332;
    color: #f5f0e8;
    font-size: 0.9rem;
    font-weight: 600;
    padding: 0.8rem 1rem;
    margin-bottom: 1rem;
    border-radius: 8px;
    text-align: center;
}

.empty-state {
    color: #6b7c93;
    font-size: 0.85rem;
    text-align: center;
    padding: 1rem;
    background: #ffffff;
    border-radius: 8px;
    border: 1px solid #dde3ea;
}

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #dde3ea !important;
}

[data-testid="stSidebar"] > div {
    padding-top: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

def chat_response(user_input):
    """Call backend API for chat response"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": user_input},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data["response"]
    except requests.exceptions.RequestException as e:
        return f"Error connecting to backend: {str(e)}. Make sure backend is running at {BACKEND_URL}"

def create_new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chat_sessions[chat_id] = {
        "messages": [],
        "title": "New Chat",
        "created_at": datetime.now()
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []
    return chat_id

def switch_chat(chat_id):
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = st.session_state.chat_sessions[chat_id]["messages"]

def update_chat_title(chat_id, first_message):
    title = first_message[:30] + "..." if len(first_message) > 30 else first_message
    st.session_state.chat_sessions[chat_id]["title"] = title

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-title">💬 Chat History</div>', unsafe_allow_html=True)
    
    if st.button("🆕 New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()
    
    st.divider()
    
    if st.session_state.chat_sessions:
        for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
            is_active = chat_id == st.session_state.current_chat_id
            preview = chat_data["messages"][0]["content"][:40] + "..." if chat_data["messages"] else "Empty chat"
            
            if st.button(
                f"**{chat_data['title']}**\n{preview}",
                key=f"chat_{chat_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                switch_chat(chat_id)
                st.rerun()
    else:
        st.markdown('<div class="empty-state">No chat history yet.<br>Start a new conversation!</div>', unsafe_allow_html=True)

# Header
st.markdown('<div class="header-container"><p class="header-title">💬 RCA Chat Assistant</p></div>', unsafe_allow_html=True)

# Chat messages area
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-msg">
        <div class="welcome-icon">🤖</div>
        <div class="welcome-title">Hello! I'm your RCA Assistant</div>
        <div class="welcome-subtitle">I can help analyze error logs, troubleshoot issues, or answer technical questions.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message or paste error log..."):
    if not st.session_state.current_chat_id:
        create_new_chat()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    if len(st.session_state.messages) == 1:
        update_chat_title(st.session_state.current_chat_id, prompt)
    
    with st.spinner("Analyzing..."):
        response = chat_response(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.chat_sessions[st.session_state.current_chat_id]["messages"] = st.session_state.messages
    
    st.rerun()
