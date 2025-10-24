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

        # RAG 설정
        st.divider()
        st.subheader("RAG 설정")
        use_rag = st.checkbox(
            "RAG 활성화",
            value=st.session_state.get("use_rag", True),
            help="문서 검색 기반 답변 생성"
        )

        # RAG 상태 표시
        if "rag_client" in st.session_state:
            rag_client = st.session_state.rag_client
            if rag_client.is_available():
                st.success("✅ MCP 서버 연결됨")
                stats = rag_client.get_stats()
                if stats:
                    st.metric("문서 수", stats.get("total_documents", 0))
            else:
                st.error("❌ MCP 서버 연결 실패")

        st.divider()
        if st.button("대화 초기화"):
            return {"temperature": temperature, "use_rag": use_rag, "clear": True}

        return {"temperature": temperature, "use_rag": use_rag, "clear": False}


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
    st.caption("소상공인 마케팅 전략 추천 챗봇")


def render_competition_questions() -> Optional[dict]:
    """
    Render competition question buttons

    Returns:
        dict with 'question_type' and 'filters' if button clicked, None otherwise
    """
    st.subheader("📋 평가 문항 (B)")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏪 B-1: 카페 고객 분석", use_container_width=True):
            return {
                "question_type": "cafe_customer",
                "prompt": "카페 업종 가맹점의 주요 방문 고객 특성을 분석하고, 적합한 마케팅 채널과 홍보안을 제시해주세요.",
                "filters": {"업종": "카페"}
            }

    with col2:
        if st.button("🔄 B-2: 재방문율 향상", use_container_width=True):
            return {
                "question_type": "revisit_rate",
                "prompt": "재방문율이 낮은 가맹점의 문제점을 분석하고, 재방문율을 높일 수 있는 구체적인 마케팅 전략을 제시해주세요.",
                "filters": None
            }

    with col3:
        if st.button("🍽️ B-3: 요식업 문제 분석", use_container_width=True):
            return {
                "question_type": "restaurant_problem",
                "prompt": "요식업 가맹점의 현재 가장 큰 문제점을 데이터 기반으로 분석하고, 이를 해결할 마케팅 아이디어를 제시해주세요.",
                "filters": {"업종": "요식업"}
            }

    st.divider()
    return None
