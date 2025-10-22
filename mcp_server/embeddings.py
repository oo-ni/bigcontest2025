"""Embedding Service for Vector Generation"""

import os
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Handles text embedding generation using Sentence Transformers"""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize embedding service

        Args:
            model_name: HuggingFace model name for embeddings
                       Default uses multilingual model for Korean support
        """
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding model loaded. Dimension: {self.embedding_dim}")

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts to embeddings

        Args:
            texts: List of text strings to encode

        Returns:
            numpy array of embeddings
        """
        if not texts:
            raise ValueError("texts cannot be empty")

        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings

    def encode_single(self, text: str) -> np.ndarray:
        """
        Encode a single text to embedding

        Args:
            text: Text string to encode

        Returns:
            numpy array of single embedding
        """
        return self.encode([text])[0]

    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.embedding_dim
