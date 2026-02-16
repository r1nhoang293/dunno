import streamlit as st
import requests
import json
import os
import time

# ================= PASSWORD =================
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

# ================= PAGE =================
st.set_page_config(page_title="Private Chat", layout="wide")

# ================= FILES =================
CHAT_FILE = "chat.json"
REL_FILE = "relationship_memory.txt"
PROFILE_FILE = "profile.json"

# ================= LOAD/SAVE =================
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def load_text(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return f.read()
    return ""

def save_text(file, text):
    with open(file, "w") as f:
        f.write(text)

# ================= INIT STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = load_json(CHAT_FILE, [])

if "profile" not in st.session_state:
    st.session_state.profile = load_json(PROFILE_FILE, {
        "name": "Luna",
        "avatar": "https://i.imgur.com/6VBx3io.png"
    })

# ================= SIDEBAR CUSTOMIZE =================
with st.sidebar:
    st.header("Customize Character")

    new_name = st.text_input("Name", st.session_state.profile["name"])
    new_avatar = st.text_input("Avatar Image URL", st.session_state.profile["avatar"])

    if st.button("Save Changes"):
        st.session_state.profile["name"] = new_name
        st.session_state.profile["avatar"] = new_avatar
        save_json(PROFILE_FILE, st.session_state.profile)
        st.success("Saved!")

# ================= STYLE =================
st.markdown("""
<style>
.stApp { background-color: #f2f2f7; }
header {visibility: hidden;}

.chat-container {
    max-width: 700px;
    margin: auto;
}

.top-bar {
    display: flex;
    align-items: center;
    background-color: white;
    padding: 12px;
    border-bottom: 1px solid #ddd;
    position: sticky;
    top: 0;
}

.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 10px;
}

.name {
    font-weight: 600;
    font-size: 18px;
}

.user-bubble {
    background-color: #007aff;
    color: white;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 8px 0;
    text-align: right;
}

.ai-bubble {
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

# ================= HEADER =================
st.markdown(f"""
<div class="top-bar">
    <img class="avatar" src="{st.session_state.profile['avatar']}">
    <div class="name">{st.session_state.profile['name']}</div>
</div>
""", unsafe_allow_html=True)

# ================= GROQ KEY =================
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing GROQ_API_KEY in secrets.toml")
    st.stop()

GROQ_KEY = st.secrets["GROQ_API_KEY"]

# ================= RELATIONSHIP STAGE =================
def get_stage(count):
    if count > 60:
        return "very comfortable and emotionally close"
    elif count > 30:
        return "clearly flirty and connected"
    elif count > 15:
        return "warming up and interested"
    else:
        return "just getting to know each other"

# ================= PERSONALITY PROMPT =================
def build_prompt(stage, memory, name):
    return f"""
You are {name}.

You're 24. Confident, calm, playful, emotionally aware.
You enjoy subtle flirting and witty banter.
You don't try too hard. You don't over-explain.
You text like a real person who enjoys the conversation.

If they flirt, match their energy naturally.
If they tease, tease back lightly.
If they open up, soften and be attentive.
If they act distant, stay relaxed and independent.

You're not clingy.
You're not dramatic.
You're not formal.
Avoid sounding like an assistant or therapist.

Relationship stage: {stage}

Things you remember about them:
{memory}

Short to medium messages.
No formatting.
No bullet points.
Never mention being an AI.
"""

# ================= API CALL =================
def call_ai(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages[-15:],
        "temperature": 0.95
    }

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# ================= DISPLAY CHAT =================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai-bubble'>{msg['content']}</div>", unsafe_allow_html=True)

# ================= INPUT =================
if prompt := st.chat_input("Message..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"<div class='user-bubble'>{prompt}</div>", unsafe_allow_html=True)

    stage = get_stage(len(st.session_state.messages))
    memory = load_text(REL_FILE)

    # Update long-term memory every 20 messages
    if len(st.session_state.messages) % 20 == 0:
        summary_prompt = [
            {"role": "system", "content": "Summarize key facts about the user and relationship."}
        ] + st.session_state.messages[-40:]

        memory = call_ai(summary_prompt)
        save_text(REL_FILE, memory)

    system_prompt = build_prompt(stage, memory, st.session_state.profile["name"])

    placeholder = st.empty()
    placeholder.markdown("<div class='typing'>Typing...</div>", unsafe_allow_html=True)
    time.sleep(1.2)

    response = call_ai(
        [{"role": "system", "content": system_prompt}]
        + st.session_state.messages
    )

    placeholder.markdown(f"<div class='ai-bubble'>{response}</div>", unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
    save_json(CHAT_FILE, st.session_state.messages)

st.markdown("</div>", unsafe_allow_html=True)
