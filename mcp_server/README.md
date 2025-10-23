# MCP RAG Server

FastAPI 기반 MCP(Model Context Protocol) 서버 with FAISS 벡터 데이터베이스

## 기능

- **벡터 검색**: FAISS를 사용한 고속 유사도 검색
- **문서 인제스트**: 텍스트 데이터를 벡터 DB에 저장
- **다국어 지원**: 한국어 임베딩 모델 사용
- **RESTful API**: FastAPI 기반 REST 엔드포인트

## 설치

```bash
cd mcp_server
pip install -r requirements.txt
```

또는 프로젝트 루트에서:

```bash
pip install -e .
```

## 실행

### 개발 모드

```bash
cd mcp_server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 프로덕션 모드

```bash
cd mcp_server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 엔드포인트

### Health Check
```bash
GET /health
```

서버 상태 확인

### Query Documents
```bash
POST /query
Content-Type: application/json

{
  "query": "검색할 질문",
  "top_k": 5,
  "threshold": 0.7
}
```

벡터 DB에서 관련 문서 검색

### Ingest Document
```bash
POST /ingest
Content-Type: application/json

{
  "text": "저장할 텍스트",
  "metadata": {
    "source": "file.txt",
    "category": "카테고리"
  }
}
```

새 문서를 벡터 DB에 추가

### Save Vector Store
```bash
POST /save
```

현재 벡터 DB를 디스크에 저장

### Get Statistics
```bash
GET /stats
```

벡터 DB 통계 정보

## 데이터 인제스트

### Python 스크립트 사용

```python
from mcp_server.data_ingestion import DataIngestionPipeline, create_sample_data
from mcp_server.embeddings import EmbeddingService
from mcp_server.vector_store import VectorStore

# 서비스 초기화
embedding_service = EmbeddingService()
vector_store = VectorStore(embedding_service)

# 데이터 인제스트 파이프라인
pipeline = DataIngestionPipeline(vector_store)

# 샘플 데이터 생성
create_sample_data("./data")

# 디렉토리 전체 인제스트
pipeline.ingest_directory("./data", pattern="*.txt")

# 벡터 DB 저장
vector_store.save()
```

### 단일 파일 인제스트

```python
pipeline.ingest_file("./data/sample.txt")
```

### JSON 데이터 인제스트

```python
records = [
    {"text": "문서 내용 1", "category": "A"},
    {"text": "문서 내용 2", "category": "B"}
]
pipeline.ingest_json_records(records, text_field="text")
```

## 디렉토리 구조

```
mcp_server/
├── __init__.py
├── main.py              # FastAPI 서버
├── embeddings.py        # 임베딩 서비스
├── vector_store.py      # FAISS 벡터 스토어
├── data_ingestion.py    # 데이터 인제스트 파이프라인
├── requirements.txt     # 의존성
└── README.md
```

## 환경 설정

벡터 스토어는 기본적으로 `./vector_store` 디렉토리에 저장됩니다.

## 홈서버 배포

### Systemd 서비스 설정 (Linux)

`/etc/systemd/system/mcp-server.service`:

```ini
[Unit]
Description=MCP RAG Server
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bigcontest2025/mcp_server
ExecStart=/path/to/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

서비스 시작:
```bash
sudo systemctl enable mcp-server
sudo systemctl start mcp-server
sudo systemctl status mcp-server
```

### Docker 배포

프로젝트 루트의 `docker-compose.yml` 참조
