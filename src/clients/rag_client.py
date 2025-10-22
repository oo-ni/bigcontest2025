"""RAG Client for MCP Server Integration"""

import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RAGClient:
    """Client for interacting with MCP RAG Server"""

    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        Initialize RAG client

        Args:
            server_url: URL of the MCP server
        """
        self.server_url = server_url.rstrip('/')
        self._check_connection()

    def _check_connection(self):
        """Check if server is reachable"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("Successfully connected to MCP server")
            else:
                logger.warning(f"MCP server returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            logger.warning("RAG functionality may not work without MCP server")

    def query(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Query the RAG system for relevant documents

        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Similarity threshold

        Returns:
            List of relevant documents with scores
        """
        try:
            response = requests.post(
                f"{self.server_url}/query",
                json={
                    "query": query,
                    "top_k": top_k,
                    "threshold": threshold
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                logger.error(f"Query failed with status {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Query request failed: {e}")
            return []

    def ingest_document(self, text: str, metadata: Optional[Dict] = None) -> bool:
        """
        Ingest a document into the RAG system

        Args:
            text: Document text
            metadata: Optional metadata

        Returns:
            Success status
        """
        try:
            response = requests.post(
                f"{self.server_url}/ingest",
                json={
                    "text": text,
                    "metadata": metadata or {}
                },
                timeout=30
            )

            return response.status_code == 200

        except requests.exceptions.RequestException as e:
            logger.error(f"Ingest request failed: {e}")
            return False

    def get_stats(self) -> Dict:
        """
        Get RAG system statistics

        Returns:
            Statistics dictionary
        """
        try:
            response = requests.get(f"{self.server_url}/stats", timeout=5)

            if response.status_code == 200:
                return response.json()
            else:
                return {}

        except requests.exceptions.RequestException as e:
            logger.error(f"Stats request failed: {e}")
            return {}

    def is_available(self) -> bool:
        """
        Check if RAG server is available

        Returns:
            Availability status
        """
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


def format_rag_context(results: List[Dict], max_length: int = 2000) -> str:
    """
    Format RAG results into context string for LLM

    Args:
        results: List of RAG query results
        max_length: Maximum length of context

    Returns:
        Formatted context string
    """
    if not results:
        return ""

    context_parts = ["다음은 관련 정보입니다:\n"]

    current_length = len(context_parts[0])

    for idx, result in enumerate(results, 1):
        text = result.get("text", "")
        score = result.get("score", 0)

        part = f"\n[문서 {idx}] (관련도: {score:.2f})\n{text}\n"

        if current_length + len(part) > max_length:
            break

        context_parts.append(part)
        current_length += len(part)

    return "".join(context_parts)
