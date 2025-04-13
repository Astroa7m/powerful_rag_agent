import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from fake_data.fake_memory import get_user_session
from hybird_rag import agent_with_chat_history, config

st.set_page_config(page_title="AOU Assistant Chat", layout="wide")

# Redirect to login if no session
user = get_user_session()
if not user:
    st.warning("You must log in first.")
    st.stop()

col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title(f"🤖 Welcome {user['name']}! Ask me anything about AOU ✨")
with col2:
    if st.button("Logout"):
        st.session_state.clear()

# Chat interface
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.chat_message("assistant"):
    st.markdown("How can I help you today?")

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

user_input = st.chat_input("Ask a question...")
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = agent_with_chat_history.invoke({"input": user_input}, config=config)
            answer = response["output"] if isinstance(response, dict) and "output" in response else str(response)
            st.markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
