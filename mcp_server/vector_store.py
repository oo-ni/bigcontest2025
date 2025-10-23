"""FAISS Vector Store Implementation"""

import os
import pickle
import json
from typing import List, Dict, Optional
import numpy as np
import faiss
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for document retrieval"""

    def __init__(
        self,
        embedding_service,
        store_path: str = "./vector_store",
        index_name: str = "faiss_index"
    ):
        """
        Initialize vector store

        Args:
            embedding_service: Embedding service instance
            store_path: Path to store vector database
            index_name: Name of the index file
        """
        self.embedding_service = embedding_service
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)

        self.index_path = self.store_path / f"{index_name}.faiss"
        self.metadata_path = self.store_path / f"{index_name}_metadata.pkl"

        self.dimension = embedding_service.get_dimension()
        self.index: Optional[faiss.Index] = None
        self.documents: List[str] = []
        self.metadata: List[Dict] = []

        logger.info(f"Vector store initialized at {self.store_path}")

    def _initialize_index(self):
        """Initialize FAISS index"""
        # Use IndexFlatL2 for exact search (can be changed to IVF for large datasets)
        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info(f"Created new FAISS index with dimension {self.dimension}")

    def add_document(self, text: str, metadata: Optional[Dict] = None) -> str:
        """
        Add a document to the vector store

        Args:
            text: Document text
            metadata: Optional metadata dictionary

        Returns:
            Document ID (index)
        """
        if self.index is None:
            self._initialize_index()

        # Generate embedding
        embedding = self.embedding_service.encode_single(text)
        embedding = embedding.reshape(1, -1).astype('float32')

        # Add to FAISS index
        self.index.add(embedding)

        # Store document and metadata
        doc_id = len(self.documents)
        self.documents.append(text)
        self.metadata.append(metadata or {})

        logger.info(f"Added document {doc_id} to vector store")
        return str(doc_id)

    def add_documents(self, texts: List[str], metadatas: Optional[List[Dict]] = None):
        """
        Add multiple documents to the vector store

        Args:
            texts: List of document texts
            metadatas: Optional list of metadata dictionaries
        """
        if not texts:
            return

        if self.index is None:
            self._initialize_index()

        # Generate embeddings
        embeddings = self.embedding_service.encode(texts)
        embeddings = embeddings.astype('float32')

        # Add to FAISS index
        self.index.add(embeddings)

        # Store documents and metadata
        self.documents.extend(texts)

        if metadatas:
            self.metadata.extend(metadatas)
        else:
            self.metadata.extend([{}] * len(texts))

        logger.info(f"Added {len(texts)} documents to vector store")

    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Search for similar documents

        Args:
            query: Search query text
            top_k: Number of results to return
            threshold: Similarity threshold (0-1, higher is more similar)

        Returns:
            List of results with text, metadata, and score
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []

        # Generate query embedding
        query_embedding = self.embedding_service.encode_single(query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')

        # Search FAISS index
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

        # Convert distances to similarity scores (L2 distance -> similarity)
        # Normalize by converting to cosine similarity approximation
        similarities = 1 / (1 + distances[0])

        # Filter by threshold and prepare results
        results = []
        for idx, similarity in zip(indices[0], similarities):
            if idx >= 0 and similarity >= threshold:
                results.append({
                    "text": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": float(similarity),
                    "doc_id": int(idx)
                })

        logger.info(f"Found {len(results)} results for query")
        return results

    def save(self):
        """Save index and metadata to disk"""
        if self.index is None:
            logger.warning("No index to save")
            return

        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))

        # Save metadata and documents
        with open(self.metadata_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)

        logger.info(f"Saved vector store to {self.store_path}")

    def load(self):
        """Load index and metadata from disk"""
        if not self.index_path.exists():
            logger.info("No existing index found, creating new one")
            self._initialize_index()
            return

        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))

            # Load metadata and documents
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadata = data['metadata']

            logger.info(f"Loaded vector store with {self.index.ntotal} documents")
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            logger.info("Creating new index")
            self._initialize_index()

    def is_loaded(self) -> bool:
        """Check if vector store is loaded and ready"""
        return self.index is not None

    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        if self.index is None:
            return {
                "total_documents": 0,
                "dimension": self.dimension,
                "loaded": False
            }

        return {
            "total_documents": self.index.ntotal,
            "dimension": self.dimension,
            "loaded": True,
            "store_path": str(self.store_path)
        }

    def clear(self):
        """Clear all documents from the vector store"""
        self._initialize_index()
        self.documents = []
        self.metadata = []
        logger.info("Cleared vector store")
