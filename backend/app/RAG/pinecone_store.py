"""
Pinecone Vector Store Service - LegalContractAI RAG Layer

Provides a lazy-initialized, singleton PineconeService that wraps langchain-pinecone
to perform similarity search over legal document indexes.

Usage:
    from app.RAG.pinecone_store import pinecone_service
    vector_store = pinecone_service.get_vector_store("indian-statutes-v2")
    docs = vector_store.similarity_search_with_score("termination clause", k=3)
"""

import logging
import os
from typing import Optional

from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

logger = logging.getLogger(__name__)


class PineconeService:
    """
    Lazy-initialized singleton service for Pinecone vector store access.

    Connects once on first use and caches vector store instances per index name
    to avoid redundant re-connections.
    """

    def __init__(self):
        self._pc: Optional[Pinecone] = None
        self._embeddings: Optional[OpenAIEmbeddings] = None
        self._stores: dict[str, PineconeVectorStore] = {}

    def _ensure_initialized(self) -> None:
        """Initialize Pinecone client and embeddings model on first call."""
        if self._pc is not None:
            return

        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "PINECONE_API_KEY environment variable is not set. "
                "RAG features will be unavailable."
            )

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is not set. "
                "Embeddings model cannot be initialised."
            )

        try:
            self._pc = Pinecone(api_key=api_key)
            # text-embedding-3-small is cost-effective and 1536-dim compatible
            self._embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=openai_api_key,
            )
            logger.info("PineconeService initialised successfully.")
        except Exception as exc:
            # Reset so next call retries
            self._pc = None
            self._embeddings = None
            raise RuntimeError(f"Failed to initialise PineconeService: {exc}") from exc

    def get_vector_store(self, index_name: str) -> PineconeVectorStore:
        """
        Return a (cached) LangChain PineconeVectorStore for the given index.

        Args:
            index_name: Name of the Pinecone index to connect to.

        Returns:
            A PineconeVectorStore instance ready for similarity search.

        Raises:
            RuntimeError: If required API keys are missing or connection fails.
        """
        if index_name in self._stores:
            return self._stores[index_name]

        self._ensure_initialized()

        try:
            store = PineconeVectorStore(
                index=self._pc.Index(index_name),
                embedding=self._embeddings,
                text_key="text",
            )
            self._stores[index_name] = store
            logger.info("Connected to Pinecone index: %s", index_name)
            return store
        except Exception as exc:
            raise RuntimeError(
                f"Failed to connect to Pinecone index '{index_name}': {exc}"
            ) from exc


# Singleton – imported by agents as `from app.RAG.pinecone_store import pinecone_service`
pinecone_service = PineconeService()
