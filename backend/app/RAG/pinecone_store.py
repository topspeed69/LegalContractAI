"""
Pinecone Vector Store Service - LegalContractAI RAG Layer

Provides a lazy-initialized, singleton PineconeService that performs
semantic search using Pinecone's server-side integrated inference.
"""

import logging
import os
from typing import Any, Dict, List, Optional
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class PineconeService:
    """
    Lazy-initialized singleton service for Pinecone vector store access.
    """

    def __init__(self):
        self._pc = None

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

    def search(self, index_name: str, query: str, k: int = 5, namespace: str = "legal-docs", filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Perform semantic search using Pinecone Integrated Inference.
        Returns a list of LangChain-style Document objects for compatibility.
        """
        try:
            self._ensure_initialized()
            index = self._pc.Index(index_name)
            
            # Use query with inputs for integrated inference in SDK 5.0.x
            # This allows passing raw text instead of vectors.
            results = index.query(
                namespace=namespace,
                top_k=k,
                inputs={"text": query},
                filter=filter,
                include_metadata=True
            )
            
            docs = []
            for match in results.get("matches", []):
                # Integrated inference results usually place content in metadata
                metadata = match.get("metadata", {})
                content = metadata.get("text", "") # Standard field name we use
                
                docs.append(Document(
                    page_content=content,
                    metadata=metadata
                ))
            
            logger.info(f"Retrieved {len(docs)} documents from {index_name}")
            return docs
            
        except Exception as exc:
            logger.error(f"Pinecone search failed for index {index_name}: {exc}")
            return []


# Singleton instance
pinecone_service = PineconeService()
