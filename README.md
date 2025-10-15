# BigContest 2025 Project

BigContest 2025 프로젝트 - Streamlit + MCP 서버

## 기술 스택

- Python 3.10+
- [Streamlit](https://streamlit.io/) - 데이터 앱 프레임워크
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
- [uv](https://github.com/astral-sh/uv) - 빠른 Python 패키지 관리자
- Docker (선택사항)

## 프로젝트 구조

```
bigcontest2025/
├── .streamlit/         # Streamlit 설정
│   └── config.toml
├── .venv/              # 가상환경 (로컬)
├── app.py              # Streamlit 메인 애플리케이션
├── main.py             # 기타 스크립트
├── pyproject.toml      # 프로젝트 설정 및 의존성
├── uv.lock             # 의존성 버전 고정 파일
├── .env.dev            # 개발 환경 변수
├── .env.prod           # 프로덕션 환경 변수
├── Dockerfile          # Docker 이미지 빌드 파일
└── docker-compose.yml  # Docker Compose 설정
```

## 설치 및 실행

### 1. 의존성 설치

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 패키지 설치
uv sync
```

### 2. 환경별 실행

**개발 환경 (.env.dev 사용)**
```bash
uv run --env-file .env.dev streamlit run app.py
```

**프로덕션 환경 (.env.prod 사용)**
```bash
uv run --env-file .env.prod streamlit run app.py
```

앱이 실행되면 브라우저에서 `http://localhost:8501`로 접속하세요.

### 3. Docker 실행 (선택사항)

```bash
docker-compose up --build
```

## 환경 변수 설정

프로젝트는 `.env.dev`와 `.env.prod` 두 개의 환경 파일을 사용합니다:

- **`.env.dev`**: 로컬 개발용 설정 (Git 커밋됨)
- **`.env.prod`**: 프로덕션 배포용 설정 (Git 커밋됨)

API 키 등 민감한 정보는 각 파일에서 플레이스홀더를 실제 값으로 교체하거나, 배포 플랫폼의 환경 변수 설정을 사용하세요.

## 개발 가이드

### 패키지 추가
```bash
uv add pandas numpy  # 새 패키지 설치
```

### 코드 포맷팅
```bash
uv run black .        # 코드 포맷팅
uv run ruff check .   # 린팅
```

## Streamlit Cloud 배포

1. GitHub에 코드 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. 레포지토리 연결
4. Secrets에서 환경 변수 설정 (`.env.prod` 참고)
5. 배포 완료!

## 라이선스

[라이선스 정보 추가]
