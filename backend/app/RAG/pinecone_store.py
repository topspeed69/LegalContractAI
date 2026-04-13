"""
Pinecone Vector Store Service - LegalContractAI RAG Layer

Provides a lazy-initialized, singleton PineconeService that wraps langchain-pinecone
to perform similarity search over legal document indexes.

This implementation uses Pinecone's server-side inference (embeddings) by default.
"""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PineconeService:
    """
    Lazy-initialized singleton service for Pinecone vector store access.
    """

    def __init__(self):
        self._pc = None
        self._stores: Dict[str, Any] = {}

    def _ensure_initialized(self) -> None:
        """Initialize Pinecone client on first call."""
        if self._pc is not None:
            return

        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY is not set.")

        from pinecone import Pinecone
        self._pc = Pinecone(api_key=api_key)
        logger.info("Pinecone client initialised.")

    def get_vector_store(self, index_name: str):
        """
        Return a (cached) LangChain PineconeVectorStore for the given index.
        Uses Pinecone server-side inference by default.
        """
        if index_name in self._stores:
            return self._stores[index_name]

        self._ensure_initialized()

        from langchain_pinecone import PineconeVectorStore

        try:
            # According to user instruction, use Pinecone's inference as default.
            # Passing embedding=None to PineconeVectorStore tells it to use 
            # the index's integrated inference model.
            store = PineconeVectorStore(
                index=self._pc.Index(index_name),
                embedding=None,  # type: ignore
                text_key="text"
            )
            self._stores[index_name] = store
            logger.info("Connected to Pinecone index with native inference: %s", index_name)
            return store
        except Exception as exc:
            logger.error("Failed to connect to index %s: %s", index_name, exc)
            raise RuntimeError(f"Pinecone connection error: {exc}")


# Singleton instance
pinecone_service = PineconeService()
