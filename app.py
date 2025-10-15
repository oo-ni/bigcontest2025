"""BigContest 2025 - Streamlit Chat Application"""

import streamlit as st
from dotenv import load_dotenv

from src.config import Config
from src.clients.gemini import GeminiClient
from src.session import ChatSession
from src.ui import (
    render_page_config,
    render_header,
    render_sidebar_settings,
    render_chat_history,
    render_input_box,
    render_chat_message,
)

load_dotenv()


def initialize_session_state() -> None:
    """Initialize Streamlit session state"""
    if "session" not in st.session_state:
        st.session_state.session = ChatSession()
    if "config" not in st.session_state:
        st.session_state.config = Config()
    if "client" not in st.session_state:
        config = st.session_state.config
        st.session_state.client = GeminiClient(
            api_key=config.get_api_key(),
            model=config.get_model_name(),
            temperature=config.get_temperature(),
        )


def handle_settings(settings: dict) -> None:
    """Handle sidebar settings changes"""
    if settings["clear"]:
        st.session_state.session.clear_messages()
        st.rerun()

    current_temp = st.session_state.config.get_temperature()
    if settings["temperature"] != current_temp:
        st.session_state.config.modify_temperature(settings["temperature"])
        st.session_state.client.modify_temperature(settings["temperature"])


def handle_user_input(user_input: str) -> None:
    """Handle user message and generate response"""
    session = st.session_state.session
    client = st.session_state.client

    session.add_message("user", user_input)
    render_chat_message("user", user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        for chunk in client.stream_generate(user_input):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    session.add_message("assistant", full_response)


def main() -> None:
    """Main application entry point"""
    render_page_config()
    initialize_session_state()

    render_header()
    settings = render_sidebar_settings()
    handle_settings(settings)

    render_chat_history(st.session_state.session.get_messages())

    if user_input := render_input_box():
        handle_user_input(user_input)


if __name__ == "__main__":
    main()
