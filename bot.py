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

# ==========
