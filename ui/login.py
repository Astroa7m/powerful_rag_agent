import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from streamlit_extras.switch_page_button import switch_page  # <-- Add this line
from fake_data.auth import authenticate_user
from fake_data.fake_api import get_user_profile
from fake_data.fake_memory import get_user_session, set_user_session

st.set_page_config(page_title="AOU Assistant Login", layout="centered")

# Redirect if already logged in
if get_user_session():
    st.success(f"Welcome back, {get_user_session()['name']}!")
    st.write("Main interface placeholder ✨")
    st.stop()

st.title("🔐 AOU Assistant Login")

with st.form("login_form"):
    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

if submitted:
    if authenticate_user(user_id, password):
        user_data = get_user_profile(user_id)
        if user_data:
            set_user_session(user_data)
            switch_page("home")  # must match the page name (home.py → "home")
        else:
            st.error("User profile not found.")
    else:
        st.error("Invalid credentials. Try again.")
