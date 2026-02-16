import streamlit as st
import requests
import json
import os
import time

# -------------------------------------------------
# 🔒 PASSWORD PROTECTION
# -------------------------------------------------
PASSWORD = "123123"

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

# -------------------------------------------------
# 🧿 PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Luna 💕", page_icon="💕", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1a001f, #330033);
    color: #ffffff;
}
section[data-testid="stSidebar"] {
    background-color: #140014;
}
</style>
""", unsafe_allow_html=True)

st.title("💕 Luna")

# -------------------------------------------------
# 🔥 SPICE LEVEL
# -------------------------------------------------
spice_level = st.sidebar.slider("Spice Level 🔥", 1, 5, 3)

# -------------------------------------------------
# 🔑 API KEY CHECK
# -------------------------------------------------
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing GROQ_API_KEY in Streamlit Cloud Secrets")
    st.stop()

GROQ_KEY = st.secrets["GROQ_API_KEY"]

# -------------------------------------------------
# 💾 MEMORY FILE
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
# 💕 RELATIONSHIP STAGE
# -------------------------------------------------
def get_relationship_stage(message_count):
    if message_count > 40:
        return "very comfortable and emotionally close"
    elif message_count > 20:
        return "clearly flirty and building tension"
    elif message_count > 10:
        return "playfully interested"
    else:
        return "just getting to know each other"

# -------------------------------------------------
# 🧠 SYSTEM PROMPT BUILDER
# -------------------------------------------------
def build_system_prompt(spice_level, relationship_stage):
    return f"""
You are Luna.

You are confident, playful, and flirtatious.
The relationship stage is: {relationship_stage}.

Spice level is {spice_level}/5.
At low spice: sweet and teasing.
At high spice: bold, intense tension, dominant energy (never explicit).

You text casually and naturally.
You react emotionally to what the user says.
You sometimes tease, challenge, or escalate tension.
You remember past conversations and refer back to them naturally.

Never break character.
Never mention being an AI.
Keep responses medium length.
Build chemistry slowly but confidently.
"""

# -------------------------------------------------
# 🚀 GROQ CALL
# -------------------------------------------------
def call_luna(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages[-15:],
        "temperature": 0.9
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

# -------------------------------------------------
# 🗂 SESSION INIT
# -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()

if st.sidebar.button("Reset Relationship 💔"):
    st.session_state.messages = []
    save_memory([])
    st.rerun()

# -------------------------------------------------
# 💬 DISPLAY CHAT
# -------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# ✨ USER INPUT
# -------------------------------------------------
if prompt := st.chat_input("say something to luna..."):

    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)

    with st.chat_message("user"):
        st.markdown(prompt)

    message_count = len(st.session_state.messages)
    relationship_stage = get_relationship_stage(message_count)
    system_prompt = build_system_prompt(spice_level, relationship_stage)

    with st.chat_message("assistant"):

        response = call_luna(
            [{"role": "system", "content": system_prompt}]
            + st.session_state.messages
        )

        # ⏳ Typing delay based on spice
        time.sleep(1 + spice_level * 0.4)

        st.markdown(response)

        assistant_msg = {"role": "assistant", "content": response}
        st.session_state.messages.append(assistant_msg)

        save_memory(st.session_state.messages)
