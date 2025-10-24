"""JSONL 데이터 인제스트 스크립트

BigContest 2025 가맹점 데이터를 FAISS 벡터 DB에 저장합니다.
"""

import sys
import json
import logging
from pathlib import Path
from tqdm import tqdm

# 상위 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_server.embeddings import EmbeddingService
from mcp_server.vector_store import VectorStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_jsonl_file(
    jsonl_path: str,
    vector_store: VectorStore,
    batch_size: int = 100
):
    """
    JSONL 파일을 벡터 스토어에 인제스트

    Args:
        jsonl_path: JSONL 파일 경로
        vector_store: VectorStore 인스턴스
        batch_size: 배치 사이즈
    """
    path = Path(jsonl_path)

    if not path.exists():
        raise FileNotFoundError(f"JSONL 파일을 찾을 수 없습니다: {jsonl_path}")

    logger.info(f"JSONL 파일 읽기 시작: {jsonl_path}")

    # 먼저 총 라인 수 카운트 (진행률 표시용)
    with open(path, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)

    logger.info(f"총 {total_lines:,}개의 데이터 발견")

    # 배치로 읽어서 처리
    texts = []
    metadatas = []
    processed = 0

    with open(path, 'r', encoding='utf-8') as f:
        with tqdm(total=total_lines, desc="인제스팅") as pbar:
            for line_num, line in enumerate(f, 1):
                try:
                    # JSON 파싱
                    data = json.loads(line.strip())

                    # prompt 필드가 text가 됨
                    if 'prompt' not in data:
                        logger.warning(f"라인 {line_num}: 'prompt' 필드 없음, 건너뜀")
                        pbar.update(1)
                        continue

                    text = data['prompt']
                    metadata = data.get('metadata', {})

                    # 라인 번호 추가
                    metadata['line_number'] = line_num

                    texts.append(text)
                    metadatas.append(metadata)

                    # 배치 사이즈에 도달하면 벡터 스토어에 추가
                    if len(texts) >= batch_size:
                        vector_store.add_documents(texts, metadatas)
                        processed += len(texts)
                        texts = []
                        metadatas = []

                    pbar.update(1)

                except json.JSONDecodeError as e:
                    logger.error(f"라인 {line_num}: JSON 파싱 실패 - {e}")
                    pbar.update(1)
                    continue
                except Exception as e:
                    logger.error(f"라인 {line_num}: 처리 실패 - {e}")
                    pbar.update(1)
                    continue

    # 남은 데이터 처리
    if texts:
        vector_store.add_documents(texts, metadatas)
        processed += len(texts)

    logger.info(f"✅ 총 {processed:,}개 데이터 인제스트 완료")
    return processed


def main():
    """메인 실행 함수"""

    # 경로 설정
    project_root = Path(__file__).parent.parent.parent
    jsonl_path = project_root.parent / "jsonl_data" / "prompt_dataset.jsonl"
    vector_store_path = project_root / "vector_store"

    logger.info("=" * 60)
    logger.info("BigContest 2025 - JSONL 데이터 인제스트")
    logger.info("=" * 60)
    logger.info(f"JSONL 파일: {jsonl_path}")
    logger.info(f"벡터 스토어: {vector_store_path}")
    logger.info("=" * 60)

    # 벡터 스토어 경로 확인
    if not jsonl_path.exists():
        logger.error(f"❌ JSONL 파일을 찾을 수 없습니다: {jsonl_path}")
        logger.info("파일 경로를 확인해주세요.")
        return

    # 임베딩 서비스 초기화
    logger.info("임베딩 서비스 초기화 중...")
    embedding_service = EmbeddingService()

    # 벡터 스토어 초기화
    logger.info("벡터 스토어 초기화 중...")
    vector_store = VectorStore(
        embedding_service=embedding_service,
        store_path=str(vector_store_path)
    )

    # 기존 데이터 확인
    stats = vector_store.get_stats()
    if stats['total_documents'] > 0:
        logger.warning(f"⚠️  벡터 스토어에 이미 {stats['total_documents']:,}개 문서가 있습니다.")
        response = input("기존 데이터를 삭제하고 새로 시작하시겠습니까? (y/N): ")

        if response.lower() == 'y':
            logger.info("기존 데이터 삭제 중...")
            vector_store.clear()
        else:
            logger.info("기존 데이터에 추가합니다.")

    # JSONL 인제스트
    try:
        processed = ingest_jsonl_file(
            jsonl_path=str(jsonl_path),
            vector_store=vector_store,
            batch_size=100
        )

        # 벡터 스토어 저장
        logger.info("벡터 스토어 저장 중...")
        vector_store.save()

        # 최종 통계
        stats = vector_store.get_stats()
        logger.info("=" * 60)
        logger.info("✅ 인제스트 완료!")
        logger.info(f"총 문서 수: {stats['total_documents']:,}")
        logger.info(f"임베딩 차원: {stats['dimension']}")
        logger.info(f"저장 경로: {stats['store_path']}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ 인제스트 실패: {e}")
        raise


if __name__ == "__main__":
    main()
