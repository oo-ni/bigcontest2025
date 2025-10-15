# BigContest 2025 Project

Gemini API를 활용한 심플한 채팅 인터페이스

## 기술 스택

- Python 3.10+
- [Streamlit](https://streamlit.io/) - 데이터 앱 프레임워크
- [Google Generative AI](https://ai.google.dev/) - Gemini API
- [uv](https://github.com/astral-sh/uv) - 빠른 Python 패키지 관리자
- Docker (선택사항)

## 기능

- Gemini API 기반 실시간 채팅
- 스트리밍 응답 지원
- Temperature 조절 (0.0 ~ 2.0)
- 대화 히스토리 관리 (메모리)
- 깔끔한 UI (최소 색상, 심플 디자인)

## 프로젝트 구조

```
bigcontest2025/
├── app.py                   # Streamlit 메인 애플리케이션
├── src/
│   ├── config.py            # 설정 관리
│   ├── session.py           # 채팅 세션 관리
│   ├── ui.py                # UI 컴포넌트
│   └── clients/
│       ├── base.py          # LLM 클라이언트 인터페이스
│       └── gemini.py        # Gemini API 구현
├── .streamlit/
│   └── config.toml          # Streamlit 설정
├── .env.dev                 # 개발 환경 변수
├── .env.prod                # 프로덕션 환경 변수
├── pyproject.toml           # 프로젝트 설정 및 의존성
└── uv.lock                  # 의존성 버전 고정
```

## 설치 및 실행

### 1. uv 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Gemini API 키 설정

[Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 발급받으세요.

`.env.dev` 파일을 열고 API 키를 입력:

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. 의존성 설치

```bash
uv sync
```

### 4. 앱 실행

**개발 환경 실행**
```bash
uv run --env-file .env.dev streamlit run app.py
```

**프로덕션 환경 실행**
```bash
uv run --env-file .env.prod streamlit run app.py
```

앱이 실행되면 브라우저에서 `http://localhost:8501`로 접속하세요.

### 5. Docker 실행 (선택사항)

```bash
docker-compose up --build
```

## 환경 변수 설정

프로젝트는 `.env.dev`와 `.env.prod` 두 개의 환경 파일을 사용합니다:

- **`.env.dev`**: 로컬 개발용 설정 (Git 커밋됨, API 키는 실제 값으로 교체)
- **`.env.prod`**: 프로덕션 배포용 설정 (Git 커밋됨, 배포 플랫폼에서 실제 값 설정)

필수 환경 변수:
- `GEMINI_API_KEY`: Google Gemini API 키

## 사용법

1. 앱 실행 후 `http://localhost:8501` 접속
2. 메시지 입력창에 질문 입력
3. 실시간 스트리밍 응답 확인
4. 사이드바에서 Temperature 조절 (창의성 조절)
5. "대화 초기화" 버튼으로 채팅 히스토리 리셋

## 개발 가이드

### 패키지 추가
```bash
uv add package-name
```

### 코드 포맷팅
```bash
uv run black .        # 포맷팅
uv run ruff check .   # 린팅
```

### 다른 LLM 사용하기

`LLMClient` Protocol을 구현하여 다른 LLM으로 쉽게 전환 가능:

1. `src/clients/` 에 새 클라이언트 구현
2. `app.py`에서 클라이언트만 교체

## Streamlit Cloud 배포

1. GitHub에 코드 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. 레포지토리 연결
4. Secrets에서 `GEMINI_API_KEY` 설정
5. 배포 완료!

## 라이선스

[라이선스 정보 추가]
