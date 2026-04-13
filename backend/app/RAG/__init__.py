"""
RAG Package - Retrieval-Augmented Generation for LegalContractAI

Provides vector store access via Pinecone for semantic search over legal documents.
"""

from .pinecone_store import pinecone_service

__all__ = ["pinecone_service"]
