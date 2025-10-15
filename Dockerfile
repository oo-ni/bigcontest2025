# 빌드 스테이지
FROM python:3.11-slim AS builder

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 의존성 파일만 먼저 복사 (Docker 캐싱 활용)
COPY pyproject.toml uv.lock* ./

# 의존성 설치 (프로덕션 전용, lock 파일이 있으면 사용)
RUN uv sync --frozen --no-dev --no-cache || uv sync --no-dev --no-cache

# 런타임 스테이지
FROM python:3.11-slim

WORKDIR /app

# 빌드 스테이지에서 가상환경 복사
COPY --from=builder /app/.venv /app/.venv

# 소스 코드 복사
COPY . .

# PATH에 가상환경 추가
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Streamlit 설정
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 포트 노출
EXPOSE 8501

# Streamlit 앱 실행
CMD ["streamlit", "run", "app.py"]
