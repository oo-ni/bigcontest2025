"""UI Component Functions"""

import streamlit as st
from typing import Optional


def render_chat_message(role: str, content: str) -> None:
    """Render a single chat message"""
    with st.chat_message(role):
        st.markdown(content)


def render_chat_history(messages: list[dict]) -> None:
    """Render all chat messages"""
    for message in messages:
        render_chat_message(message["role"], message["content"])


def render_input_box() -> Optional[str]:
    """Render chat input box and return user input"""
    return st.chat_input("메시지를 입력하세요")


def render_sidebar_settings() -> dict:
    """Render sidebar settings and return configuration"""
    with st.sidebar:
        st.header("설정")

        temperature = st.slider(
            "Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1
        )

        if st.button("대화 초기화"):
            return {"temperature": temperature, "clear": True}

        return {"temperature": temperature, "clear": False}


def render_page_config() -> None:
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="BigContest 2025",
        page_icon="💬",
        layout="centered",
        initial_sidebar_state="expanded",
    )


def render_header() -> None:
    """Render page header"""
    st.title("BigContest 2025")
    st.caption("Gemini API Chat Interface")
