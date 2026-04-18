# app/api/dependencies.py
"""FastAPI依赖注入"""

from functools import lru_cache
from app.services.rag_service import RAGService
from app.services.document_service import DocumentService
from app.infrastructure.database.chroma_repository import ChromaRepository

@lru_cache()
def get_vector_repository():
    """向量仓储（单例）"""
    return ChromaRepository()


@lru_cache()
def get_document_service():
    """文档服务（单例）"""
    return DocumentService()


@lru_cache()
def get_rag_service():
    """RAG服务（单例）"""
    return RAGService(
        vector_repo=get_vector_repository(),
        document_service=get_document_service()
    )