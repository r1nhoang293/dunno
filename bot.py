import streamlit as st
import requests
import json
import os
import time
import random

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

# ================= SIDEBAR =================
with st.sidebar:
    st.header("Customize")

    new_name = st.text_input("Name", st.session_state.profile["name"])
    new_avatar = st.text_input("Avatar URL", st.session_state.profile["avatar"])

    if st.button("Save Profile"):
        st.session_state.profile["name"] = new_name
        st.session_state.profile["avatar"] = new_avatar
        save_json(PROFILE_FILE, st.session_state.profile)
        st.success("Saved!")

# ================= STYLE =================
st.markdown("""
<style>
.stApp { background-color: #f2f2f7; }
header {visibility: hidden;}

.chat-c
