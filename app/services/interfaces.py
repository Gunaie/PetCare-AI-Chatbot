# app/services/interfaces.py
"""服务接口"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..domain.models import Document


class RAGServiceInterface(ABC):
    """RAG服务接口"""
    
    @abstractmethod
    def add_document(self, file_path: str) -> Dict[str, Any]:
        """添加文档"""
        pass
    
    @abstractmethod
    def query(self, question: str) -> Dict[str, Any]:
        """查询"""
        pass
    
    @abstractmethod
    def list_documents(self) -> Dict[str, Any]:
        """列出文档"""
        pass