# 빌드 스테이지
FROM python:3.11-slim AS builder

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 의존성 파일 복사
COPY pyproject.toml ./

# uv를 사용해서 requirements.txt 생성 후 pip로 설치
RUN uv pip compile pyproject.toml -o requirements.txt && \
    python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

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
