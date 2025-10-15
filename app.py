"""
BigContest 2025 - Streamlit Application
Main entry point for the Streamlit app
"""

import streamlit as st
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="BigContest 2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """메인 애플리케이션"""
    st.title("BigContest 2025 🏆")
    st.markdown("---")

    # 사이드바
    with st.sidebar:
        st.header("설정")
        st.write(f"환경: {os.getenv('PYTHON_ENV', 'unknown')}")
        st.write(f"버전: {os.getenv('APP_VERSION', '0.1.0')}")

    # 메인 컨텐츠
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("데이터 업로드")
        uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

        if uploaded_file is not None:
            st.success("파일이 업로드되었습니다!")
            # TODO: 데이터 처리 로직 추가

    with col2:
        st.subheader("MCP 서버 상태")
        mcp_url = os.getenv("MCP_SERVER_URL", "Not configured")
        st.info(f"MCP 서버: {mcp_url}")
        # TODO: MCP 서버 연결 로직 추가

    # 푸터
    st.markdown("---")
    st.caption("BigContest 2025 Project")


if __name__ == "__main__":
    main()
