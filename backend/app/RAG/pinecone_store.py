"""
Pinecone Vector Store Service - LegalContractAI RAG Layer

Provides a lazy-initialized, singleton PineconeService that wraps langchain-pinecone
to perform similarity search over legal document indexes.

Embedding strategy (tried in order):
  1. OpenAI text-embedding-3-small  – if OPENAI_API_KEY is set
  2. Pinecone integrated inference   – if the index has a built-in embedding model
  3. Raises RuntimeError             – caught by compliance_agent, falls back to
                                       keyword search automatically

Usage:
    from app.RAG.pinecone_store import pinecone_service
    vector_store = pinecone_service.get_vector_store("indian-statutes-v2")
    docs = vector_store.similarity_search_with_score("termination clause", k=3)
"""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PineconeService:
    """
    Lazy-initialized singleton service for Pinecone vector store access.

    Connects once on first use and caches vector store instances per index
    to avoid redundant reconnections.
    """

    def __init__(self):
        self._pc = None          # pinecone.Pinecone client
        self._embeddings = None  # LangChain embeddings model (OpenAI or None)
        self._stores: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_pinecone_client(self) -> None:
        """Bootstrap the Pinecone client (requires PINECONE_API_KEY)."""
        if self._pc is not None:
            return

        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "PINECONE_API_KEY is not set – RAG features disabled."
            )

        from pinecone import Pinecone  # lazy import keeps startup fast
        self._pc = Pinecone(api_key=api_key)
        logger.info("Pinecone client initialised.")

    def _get_embeddings(self):
        """
        Return a LangChain embeddings object if OPENAI_API_KEY is available,
        otherwise return None (caller must use Pinecone integrated inference).
        """
        if self._embeddings is not None:
            return self._embeddings

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from langchain_openai import OpenAIEmbeddings
                self._embeddings = OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    openai_api_key=openai_key,
                )
                logger.info("Using OpenAI text-embedding-3-small for RAG.")
                return self._embeddings
            except Exception as exc:
                logger.warning("Could not load OpenAI embeddings: %s", exc)

        logger.info(
            "OPENAI_API_KEY not set – will use Pinecone integrated inference "
            "(index must have a built-in embedding model)."
        )
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_vector_store(self, index_name: str):
        """
        Return a (cached) LangChain PineconeVectorStore for the given index.

        Raises RuntimeError on misconfiguration (caught upstream in
        compliance_agent._fetch_rag_context which falls back to keyword search).
        """
        if index_name in self._stores:
            return self._stores[index_name]

        self._ensure_pinecone_client()

        from langchain_pinecone import PineconeVectorStore

        embeddings = self._get_embeddings()
        pinecone_index = self._pc.Index(index_name)

        if embeddings is not None:
            # Standard path: client-side embeddings via OpenAI
            store = PineconeVectorStore(
                index=pinecone_index,
                embedding=embeddings,
                text_key="text",
            )
        else:
            # Pinecone integrated inference path (serverless indexes that have
            # a built-in model configured). We pass a stub embedding object
            # because LangChain requires one; actual embedding is done server-side.
            try:
                from langchain_pinecone import PineconeVectorStore
                # Use sparse/dense inference: pass embedding=None triggers
                # PineconeVectorStore to use the index's own inference model.
                store = PineconeVectorStore(
                    index=pinecone_index,
                    embedding=None,  # type: ignore[arg-type]
                    text_key="text",
                )
            except Exception:
                raise RuntimeError(
                    f"Index '{index_name}' requires an embedding model. "
                    "Set OPENAI_API_KEY or configure Pinecone integrated inference."
                )

        self._stores[index_name] = store
        logger.info("Connected to Pinecone index: %s", index_name)
        return store


# Module-level singleton
pinecone_service = PineconeService()
