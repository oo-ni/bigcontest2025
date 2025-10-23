#!/usr/bin/env python3
"""데이터 인제스트 스크립트"""

import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_server.embeddings import EmbeddingService
from mcp_server.vector_store import VectorStore
from mcp_server.data_ingestion import DataIngestionPipeline, create_sample_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """메인 실행 함수"""
    logger.info("=== 데이터 인제스트 시작 ===")

    # 서비스 초기화
    logger.info("임베딩 서비스 초기화 중...")
    embedding_service = EmbeddingService()

    logger.info("벡터 스토어 초기화 중...")
    vector_store = VectorStore(embedding_service)

    # 기존 데이터 로드 (있는 경우)
    vector_store.load()

    # 데이터 인제스트 파이프라인
    pipeline = DataIngestionPipeline(vector_store)

    # 샘플 데이터 생성
    data_dir = project_root / "data"
    if not data_dir.exists():
        logger.info("샘플 데이터 생성 중...")
        create_sample_data(str(data_dir))

    # 데이터 인제스트
    logger.info(f"데이터 디렉토리 인제스트: {data_dir}")

    # .txt 파일 인제스트
    try:
        pipeline.ingest_directory(str(data_dir), pattern="*.txt", recursive=True)
    except Exception as e:
        logger.error(f"TXT 파일 인제스트 실패: {e}")

    # .json 파일 인제스트
    try:
        pipeline.ingest_directory(str(data_dir), pattern="*.json", recursive=True)
    except Exception as e:
        logger.error(f"JSON 파일 인제스트 실패: {e}")

    # 벡터 스토어 저장
    logger.info("벡터 스토어 저장 중...")
    vector_store.save()

    # 통계 출력
    stats = vector_store.get_stats()
    logger.info("=== 인제스트 완료 ===")
    logger.info(f"총 문서 수: {stats['total_documents']}")
    logger.info(f"벡터 차원: {stats['dimension']}")
    logger.info(f"저장 경로: {stats['store_path']}")


if __name__ == "__main__":
    main()
