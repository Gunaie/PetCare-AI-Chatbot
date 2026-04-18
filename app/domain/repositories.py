# app/domain/repositories.py
"""仓储接口：定义数据访问抽象"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .models import TextChunk, Document


class VectorRepository(ABC):
    """向量数据库仓储接口"""
    
    @abstractmethod
    def add_chunks(self, chunks: List[TextChunk]) -> None:
        """批量添加文本块"""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[TextChunk]:
        """向量相似度搜索"""
        pass
    
    @abstractmethod
    def get_document_chunks(self, document_id: str) -> List[TextChunk]:
        """获取指定文档的所有块"""
        pass
    
    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        """删除文档及其所有块"""
        pass
    
    @abstractmethod
    def list_documents(self) -> Dict[str, Any]:
        """列出所有文档统计信息"""
        pass
    
    @abstractmethod
    def exists(self, filename: str) -> bool:
        """检查文件名是否已存在"""
        pass