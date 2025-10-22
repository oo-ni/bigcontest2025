"""FastAPI MCP Server - RAG Endpoint"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging

from .vector_store import VectorStore
from .embeddings import EmbeddingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP RAG Server", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
vector_store: Optional[VectorStore] = None
embedding_service: Optional[EmbeddingService] = None


class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    top_k: int = 5
    threshold: float = 0.7


class QueryResponse(BaseModel):
    """Query response model"""
    results: List[dict]
    query: str


class DocumentRequest(BaseModel):
    """Document ingestion request model"""
    text: str
    metadata: Optional[dict] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    vector_store_loaded: bool
    embedding_service_ready: bool


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global vector_store, embedding_service

    try:
        logger.info("Initializing MCP Server...")
        embedding_service = EmbeddingService()
        vector_store = VectorStore(embedding_service=embedding_service)
        vector_store.load()
        logger.info("MCP Server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP Server: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        vector_store_loaded=vector_store is not None and vector_store.is_loaded(),
        embedding_service_ready=embedding_service is not None
    )


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query vector store for relevant documents"""
    if not vector_store or not vector_store.is_loaded():
        raise HTTPException(status_code=503, detail="Vector store not loaded")

    try:
        results = vector_store.search(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )

        return QueryResponse(
            results=results,
            query=request.query
        )
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
async def ingest_document(request: DocumentRequest):
    """Ingest a new document into vector store"""
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")

    try:
        doc_id = vector_store.add_document(
            text=request.text,
            metadata=request.metadata or {}
        )

        return {
            "status": "success",
            "document_id": doc_id,
            "message": "Document ingested successfully"
        }
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save")
async def save_vector_store():
    """Save current vector store to disk"""
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")

    try:
        vector_store.save()
        return {"status": "success", "message": "Vector store saved"}
    except Exception as e:
        logger.error(f"Save failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get vector store statistics"""
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")

    return vector_store.get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
