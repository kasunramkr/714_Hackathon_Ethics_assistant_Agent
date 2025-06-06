import streamlit as st
import requests
import json

# Load config from settings.json
with open("settings.json", "r") as f:
    config = json.load(f)

TOKEN_URL = config["TOKEN_URL"]
API_KEY = st.secrets["ibm"]["IBM_API_KEY"]
CHAT_ENDPOINT = st.secrets["ibm"]["CHAT_ENDPOINT"]

# Function to get Bearer token
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_bearer_token(api_key):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "apikey": api_key,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey"
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# Function to send message to Watsonx.ai chat agent
def get_bot_response(message, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "user", "content": message}
        ]
    }
    response = requests.post(CHAT_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "access_token" not in st.session_state:
    st.session_state.access_token = get_bearer_token(API_KEY)

# App title
col1, col2 = st.columns([1, 8])  # Adjust width ratios as needed

with col1:
    st.image("ai_icon.png", width=90)  # Replace with your image file path

with col2:
    st.markdown("## Human Ethics Assistant AI Agent")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box for user
user_input = st.chat_input("Type your message here...")

if user_input:
    # Display user's message
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Placeholder for assistant's response with loading spinner
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                token = st.session_state.access_token
                response = get_bot_response(user_input, token)
            except Exception as e:
                response = f"Error: {str(e)}"
        response_placeholder.markdown(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Clear chat button
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
    if "access_token" in st.session_state:
        del st.session_state.access_token
    st.rerun()

### updated
uploaded_file = st.file_uploader("Attach a file")

if uploaded_file is not None:
    if st.button("Upload File"):
        print("file uploaded")