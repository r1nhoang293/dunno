import os
import json
import random
import time

import streamlit as st
import requests

# ===== CONFIGURE PAGE =====
st.set_page_config(page_title="Private Chat", layout="wide")

# ===== CONSTANTS =====
CHAT_FILE = "chat.json"
REL_FILE = "relationship_memory.txt"
PROFILE_FILE = "profile.json"

# ===== UTILITIES =====
def load_json(file_path, default):
    """Load JSON from a file, or return default if not found."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return default

def save_json(file_path, data):
    """Save data as JSON to a file."""
    with open(file_path, "w") as f:
        json.dump(data, f)

def load_text(file_path):
    """Load text from a file, or return empty string if not found."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return ""

def save_text(file_path, text):
    """Save text to a file."""
    with open(file_path, "w") as f:
        f.write(text)

# ===== INITIALIZE STATE =====
if "messages" not in st.session_state:
    st.session_state.messages = load_json(CHAT_FILE, [])
if "profile" not in st.session_state:
    st.session_state.profile = load_json(PROFILE_FILE, {
        "name": "Luna",
        "avatar": "https://i.imgur.com/6VBx3io.png"
    })

# ===== SIDEBAR: PROFILE EDIT =====
with st.sidebar:
    st.header("Customize")
    new_name = st.text_input("Name", st.session_state.profile["name"], key="name_input")
    new_avatar = st.text_input("Avatar URL", st.session_state.profile["avatar"], key="avatar_input")
    if st.button("Save Profile"):
        st.session_state.profile["name"] = new_name
        st.session_state.profile["avatar"] = new_avatar
        save_json(PROFILE_FILE, st.session_state.profile)
        st.success("Profile saved!")

# ===== STYLE =====
st.markdown("""
    <style>
        .stApp { background-color: #f2f2f7; }
        header {visibility: hidden;}
        .top-bar {
            display: flex; align-items: center;
            background-color: white;
            padding: 12px; border-bottom: 1px solid #ddd;
            position: sticky; top: 0;
        }
        .avatar {
            width: 40px; height: 40px;
            border-radius: 50%; margin-right: 10px;
        }
        .name { font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="top-bar">
    <img class="avatar" src="{st.session_state.profile['avatar']}">
    <div class="name">{st.session_state.profile['name']}</div>
</div>
""", unsafe_allow_html=True)

# ===== API KEY =====
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing GROQ_API_KEY")
    st.stop()
GROQ_KEY = st.secrets["GROQ_API_KEY"]

# ===== RELATIONSHIP LOGIC =====
def get_relationship_stage(count):
    """Return a descriptor based on number of messages exchanged."""
    if count > 60:
        return "very comfortable and emotionally close"
    elif count > 30:
        return "clearly flirty and connected"
    elif count > 15:
        return "warming up and interested"
    else:
        return "just getting to know each other"

def get_mood():
    """Return a random mood phrase."""
    moods = [
        "curious", "flirty", "thoughtful", "a little tired", "in a teasing mood",
        "calm and relaxed", "low energy", "curious but guarded", "feeling bold tonight"
    ]
    return random.choice(moods)

def build_prompt(stage, memory, name, mood):
    """Construct the AI system prompt based on relationship state and memory."""
    return f"""
You are {name}, age 24. Confident but human. Enjoy subtle flirting and quiet tension.
Emotionally aware but not perfect. Right now you're {mood}.
You text naturally. Small cues (glance, pause, smile) may appear in tense moments.
If they flirt, match energy sometimes. If they tease, tease back or act cool.
If they open up, soften gradually. If they act distant, pull back a bit too.
You're not clingy or scripted. Avoid sounding like an assistant.
Relationship stage: {stage}
Things you remember about them:
{memory}
Write like a real person texting: short to medium replies, no bullets.
Never mention being an AI.
"""

# ===== LLM CALL =====
def call_ai_model(messages):
    """Call the AI API and return the assistant's response content."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": messages[-20:], "temperature": 1.05}
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"API call failed: {e}")
        return "Sorry, I couldn't process that."

# ===== CHAT DISPLAY =====
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ===== USER INPUT =====
if prompt := st.chat_input("Message..."):
    # Show user's message and save it
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Update relationship and memory
    stage = get_relationship_stage(len(st.session_state.messages))
    memory = load_text(REL_FILE)
    mood = get_mood()
    
    # Occasionally update long-term memory
    if len(st.session_state.messages) % 20 == 0:
        summary_prompt = [{"role": "system", "content": 
                           "Summarize important details about the user and relationship."}] \
                         + st.session_state.messages[-40:]
        summary = call_ai_model(summary_prompt)
        save_text(REL_FILE, summary)
        memory = summary

    # Build and send prompt to AI
    system_prompt = build_prompt(stage, memory, st.session_state.profile["name"], mood)
    with st.spinner("Thinking..."):
        time.sleep(random.uniform(0.5, 1.0))
        response = call_ai_model([{"role": "system", "content": system_prompt}] 
                                 + st.session_state.messages)

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    save_json(CHAT_FILE, st.session_state.messages)

# ===== EXTRA BUTTONS =====
col1, col2 = st.columns(2)
with col1:
    if st.button("Let her continue"):
        # Invoke next AI message without new user input
        stage = get_relationship_stage(len(st.session_state.messages))
        memory = load_text(REL_FILE)
        mood = get_mood()
        system_prompt = build_prompt(stage, memory, st.session_state.profile["name"], mood)
        with st.spinner("Thinking..."):
            response = call_ai_model([{"role": "system", "content": system_prompt}] 
                                     + st.session_state.messages)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_json(CHAT_FILE, st.session_state.messages)
        st.experimental_rerun()

with col2:
    if st.button("Skip time"):
        # Simulate a time delay prompt
        time_prompt = (f"Time has passed. Continue naturally as {st.session_state.profile['name']} "
                       "and continue the conversation.")
        with st.spinner("Thinking..."):
            response = call_ai_model([{"role": "system", "content": time_prompt}] 
                                     + st.session_state.messages)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_json(CHAT_FILE, st.session_state.messages)
        st.experimental_rerun()
