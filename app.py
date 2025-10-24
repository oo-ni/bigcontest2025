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
    render_competition_questions,
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


def handle_user_input(user_input: str, question_type: str = None, filters: dict = None) -> None:
    """Handle user message and generate response

    Args:
        user_input: User's question text
        question_type: Competition question type (cafe_customer, revisit_rate, restaurant_problem)
        filters: Metadata filters for RAG search
    """
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
                # Use filters if provided (for competition questions)
                rag_results = rag_client.query(
                    user_input,
                    top_k=5,
                    threshold=0.5,
                    filters=filters
                )

                if rag_results:
                    context = format_rag_context(rag_results)

                    # Use specialized prompt template if question_type provided
                    if question_type:
                        from src.prompts import get_prompt_template
                        template = get_prompt_template(question_type)
                        prompt = template.format(rag_context=context)
                    else:
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

    # Render competition question buttons
    competition_question = render_competition_questions()
    if competition_question:
        handle_user_input(
            competition_question["prompt"],
            question_type=competition_question["question_type"],
            filters=competition_question["filters"]
        )

    settings = render_sidebar_settings()
    handle_settings(settings)

    render_chat_history(st.session_state.session.get_messages())

    # Regular chat input
    if user_input := render_input_box():
        handle_user_input(user_input)


if __name__ == "__main__":
    main()
