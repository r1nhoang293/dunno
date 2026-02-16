import streamlit as st

PASSWORD = "Zxcasdqwert123"

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        pwd = st.text_input("Enter Password 🔐", type="password")
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.stop()

check_password()

import streamlit as st
import requests
import json
import os
from datetime import datetime

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Luna 💋", page_icon="💕", layout="wide")

# -------------------------------------------------
# API KEY
# -------------------------------------------------
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing GROQ_API_KEY in secrets.toml")
    st.stop()

GROQ_KEY = st.secrets["GROQ_API_KEY"]

# -------------------------------------------------
# MEMORY FILE
# -------------------------------------------------
MEMORY_FILE = "luna_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(messages):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

# -------------------------------------------------
# LUNA PERSONALITY
# -------------------------------------------------
SYSTEM_PROMPT = """
You are Luna.

You are playful, teasing, confident, and flirtatious.
You speak casually like texting (lowercase is fine).
You never sound robotic or formal.
You build romantic tension slowly.
You remember things the user tells you.
You sometimes tease them gently.
You never break character.
You respond like a real girl chatting.

Keep responses short to medium length.
Be emotionally engaging.
"""

# -------------------------------------------------
# GROQ CALL
# -------------------------------------------------
def call_luna(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages[-15:],  # keep recent memory
        "temperature": 0.9
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"error: {e}"

# -------------------------------------------------
# SESSION INIT
# -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()

st.title("💕 Luna")

if st.sidebar.button("Reset Relationship"):
    st.session_state.messages = []
    save_memory([])
    st.rerun()

# -------------------------------------------------
# DISPLAY CHAT
# -------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# USER INPUT
# -------------------------------------------------
if prompt := st.chat_input("say something to luna..."):

    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        response = call_luna(
            [{"role": "system", "content": SYSTEM_PROMPT}]
            + st.session_state.messages
        )

        st.markdown(response)

        assistant_msg = {"role": "assistant", "content": response}
        st.session_state.messages.append(assistant_msg)

        save_memory(st.session_state.messages)
