"""Data Ingestion Pipeline for RAG System"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataIngestionPipeline:
    """Pipeline for ingesting various data formats into vector store"""

    def __init__(self, vector_store, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize data ingestion pipeline

        Args:
            vector_store: VectorStore instance
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks
        """
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap

        return chunks

    def ingest_text(self, text: str, metadata: Optional[Dict] = None):
        """
        Ingest plain text into vector store

        Args:
            text: Text to ingest
            metadata: Optional metadata
        """
        chunks = self.chunk_text(text)
        metadatas = [metadata or {} for _ in chunks]

        self.vector_store.add_documents(chunks, metadatas)
        logger.info(f"Ingested text in {len(chunks)} chunks")

    def ingest_file(self, file_path: str, metadata: Optional[Dict] = None):
        """
        Ingest a file into vector store

        Args:
            file_path: Path to file
            metadata: Optional metadata
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Add file info to metadata
        file_metadata = metadata or {}
        file_metadata.update({
            "source": str(path),
            "filename": path.name,
            "file_type": path.suffix
        })

        # Read file based on type
        if path.suffix == '.txt':
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.ingest_text(text, file_metadata)

        elif path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle JSON as text
            if isinstance(data, dict):
                text = json.dumps(data, ensure_ascii=False, indent=2)
            elif isinstance(data, list):
                # Ingest each item separately
                for idx, item in enumerate(data):
                    item_metadata = file_metadata.copy()
                    item_metadata['item_index'] = idx
                    text = json.dumps(item, ensure_ascii=False, indent=2)
                    self.ingest_text(text, item_metadata)
                return
            else:
                text = str(data)

            self.ingest_text(text, file_metadata)

        else:
            # Try to read as text
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.ingest_text(text, file_metadata)
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")
                raise

        logger.info(f"Ingested file: {file_path}")

    def ingest_directory(
        self,
        directory_path: str,
        pattern: str = "*.txt",
        recursive: bool = True
    ):
        """
        Ingest all files in a directory

        Args:
            directory_path: Path to directory
            pattern: File pattern to match (e.g., "*.txt", "*.json")
            recursive: Whether to search recursively
        """
        path = Path(directory_path)

        if not path.exists() or not path.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory_path}")

        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))

        logger.info(f"Found {len(files)} files matching pattern '{pattern}'")

        for file_path in files:
            try:
                self.ingest_file(str(file_path))
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
                continue

        logger.info(f"Completed ingestion of {len(files)} files")

    def ingest_json_records(
        self,
        records: List[Dict],
        text_field: str = "text",
        metadata_fields: Optional[List[str]] = None
    ):
        """
        Ingest JSON records where each record has a text field

        Args:
            records: List of dictionary records
            text_field: Field name containing text
            metadata_fields: Fields to include in metadata
        """
        texts = []
        metadatas = []

        for idx, record in enumerate(records):
            if text_field not in record:
                logger.warning(f"Record {idx} missing text field '{text_field}', skipping")
                continue

            text = record[text_field]
            metadata = {"record_index": idx}

            if metadata_fields:
                for field in metadata_fields:
                    if field in record:
                        metadata[field] = record[field]
            else:
                # Include all fields except text
                metadata.update({k: v for k, v in record.items() if k != text_field})

            texts.append(text)
            metadatas.append(metadata)

        self.vector_store.add_documents(texts, metadatas)
        logger.info(f"Ingested {len(texts)} records")


def create_sample_data(data_path: str = "./data"):
    """
    Create sample data files for testing

    Args:
        data_path: Path to create sample data
    """
    path = Path(data_path)
    path.mkdir(parents=True, exist_ok=True)

    # Sample text file
    sample_text = """
    빅콘테스트 2025는 데이터 분석 경진대회입니다.
    참가자들은 주어진 데이터를 분석하고 인사이트를 도출합니다.
    RAG 시스템을 활용하면 대용량 문서에서 관련 정보를 빠르게 검색할 수 있습니다.
    """

    with open(path / "sample1.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)

    # Sample JSON file
    sample_json = [
        {
            "id": 1,
            "title": "RAG 시스템 소개",
            "text": "RAG(Retrieval-Augmented Generation)는 정보 검색과 생성 모델을 결합한 기술입니다.",
            "category": "기술"
        },
        {
            "id": 2,
            "title": "FAISS 벡터 데이터베이스",
            "text": "FAISS는 Facebook에서 개발한 효율적인 유사도 검색 라이브러리입니다.",
            "category": "도구"
        }
    ]

    with open(path / "sample_data.json", "w", encoding="utf-8") as f:
        json.dump(sample_json, f, ensure_ascii=False, indent=2)

    logger.info(f"Created sample data in {data_path}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    from .embeddings import EmbeddingService
    from .vector_store import VectorStore

    # Initialize services
    embedding_service = EmbeddingService()
    vector_store = VectorStore(embedding_service)

    # Create sample data
    create_sample_data()

    # Ingest data
    pipeline = DataIngestionPipeline(vector_store)
    pipeline.ingest_directory("./data")

    # Save vector store
    vector_store.save()

    print("Data ingestion completed!")
