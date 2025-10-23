"""BigContest 2025 - Streamlit Chat Application"""

import streamlit as st
from dotenv import load_dotenv

from src.config import Config
from src.clients.gemini import GeminiClient
from src.clients.rag_client import RAGClient, format_rag_context
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
    if "rag_client" not in st.session_state:
        config = st.session_state.config
        st.session_state.rag_client = RAGClient(server_url=config.get_mcp_server_url())
        st.session_state.use_rag = config.get_use_rag()


def handle_settings(settings: dict) -> None:
    """Handle sidebar settings changes"""
    if settings["clear"]:
        st.session_state.session.clear_messages()
        st.rerun()

    current_temp = st.session_state.config.get_temperature()
    if settings["temperature"] != current_temp:
        st.session_state.config.modify_temperature(settings["temperature"])
        st.session_state.client.modify_temperature(settings["temperature"])

    # Handle RAG toggle
    if "use_rag" in settings:
        st.session_state.use_rag = settings["use_rag"]


def handle_user_input(user_input: str) -> None:
    """Handle user message and generate response"""
    session = st.session_state.session
    client = st.session_state.client
    rag_client = st.session_state.rag_client
    use_rag = st.session_state.use_rag

    session.add_message("user", user_input)
    render_chat_message("user", user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # RAG 활성화 시 관련 문서 검색
        prompt = user_input
        if use_rag and rag_client.is_available():
            with st.spinner("관련 문서 검색 중..."):
                rag_results = rag_client.query(user_input, top_k=3, threshold=0.5)

                if rag_results:
                    context = format_rag_context(rag_results)
                    prompt = f"{context}\n\n사용자 질문: {user_input}\n\n위 문서를 참고하여 답변해주세요."

        for chunk in client.stream_generate(prompt):
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
