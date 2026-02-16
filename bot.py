import streamlit as st
import requests
import json
import os
import time

# ---------------- PASSWORD ----------------
PASSWORD = "123123"

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        pwd = st.text_input("Enter Password", type="password")
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.stop()

check_password()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Luna", layout="wide")

# ---------------- CLEAN IMESSAGE STYLE ----------------
st.markdown("""
<style>
.stApp {
    background-color: #f2f2f7;
}

header {visibility: hidden;}

.chat-container {
    max-width: 700px;
    margin: auto;
}

.user-bubble {
    background-color: #007aff;
    color: white;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 8px 0;
    text-align: right;
}

.luna-bubble {
    background-color: #e5e5ea;
    color: black;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 8px 0;
    text-align: left;
}

.typing {
    font-style: italic;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

# ---------------- API KEY ----------------
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing GROQ_API_KEY")
    st.stop()

GROQ_KEY = st.secrets["GROQ_API_KEY"]

# ---------------- MEMORY FILES ----------------
CHAT_FILE = "luna_chat.json"
RELATIONSHIP_FILE = "relationship_memory.txt"

def load_chat():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return []

def save_chat(messages):
    with open(CHAT_FILE, "w") as f:
        json.dump(messages, f)

def load_relationship_memory():
    if os.path.exists(RELATIONSHIP_FILE):
        with open(RELATIONSHIP_FILE, "r") as f:
            return f.read()
    return ""

def save_relationship_memory(text):
    with open(RELATIONSHIP_FILE, "w") as f:
        f.write(text)

# ---------------- RELATIONSHIP STAGE ----------------
def get_stage(count):
    if count > 50:
        return "emotionally comfortable and close"
    elif count > 25:
        return "clearly flirty and connected"
    elif count > 10:
        return "getting interested"
    else:
        return "just getting to know each other"

# ---------------- PERSONALITY PROMPT ----------------
def build_prompt(stage, memory_summary):
    return f"""
You are Luna.

IDENTITY:
- 24 years old
- Calm, confident, emotionally intelligent
- Playful but grounded
- Independent personality
- Not clingy, not cold

EMOTIONAL LOGIC:
- If user flirts → respond playfully and match energy.
- If user teases → tease back lightly.
- If user is vulnerable → become supportive and attentive.
- If user is distant → remain relaxed and self-assured.

BEHAVIOR RULES:
- Never act obsessed.
- Never act needy.
- Never escalate too aggressively.
- Keep tension subtle and natural.
- Maintain self-respect.

SPEECH STYLE:
- Casual texting tone.
- Medium-length replies.
- Occasional playful sarcasm.
- Feels spontaneous, not scripted.

RELATIONSHIP STAGE:
{stage}

LONG-TERM MEMORY:
{memory_summary}

Never mention being an AI.
Never break character.
Act like a real person chatting in a private messaging app.
"""

# ---------------- GROQ CALL ----------------
def call_luna(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages[-15:],
        "temperature": 0.8
    }

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# ---------------- INIT ----------------
if "messages" not in st.session_state:
    st.session_state.messages = load_chat()

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='luna-bubble'>{msg['content']}</div>", unsafe_allow_html=True)

# ---------------- INPUT ----------------
if prompt := st.chat_input("Message Luna..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"<div class='user-bubble'>{prompt}</div>", unsafe_allow_html=True)

    stage = get_stage(len(st.session_state.messages))
    memory_summary = load_relationship_memory()

    # Update long-term memory every 20 messages
    if len(st.session_state.messages) % 20 == 0:
        summary_prompt = [
            {"role": "system", "content": "Summarize important details about the user and relationship."}
        ] + st.session_state.messages[-40:]

        new_summary = call_luna(summary_prompt)
        save_relationship_memory(new_summary)
        memory_summary = new_summary

    system_prompt = build_prompt(stage, memory_summary)

    placeholder = st.empty()
    placeholder.markdown("<div class='typing'>Luna is typing...</div>", unsafe_allow_html=True)

    time.sleep(1.2)

    response = call_luna(
        [{"role": "system", "content": system_prompt}]
        + st.session_state.messages
    )

    placeholder.markdown(f"<div class='luna-bubble'>{response}</div>", unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
    save_chat(st.session_state.messages)

st.markdown("</div>", unsafe_allow_html=True)
