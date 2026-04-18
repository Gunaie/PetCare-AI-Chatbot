# app/infrastructure/ai/base.py
"""AI服务接口定义"""

from abc import ABC, abstractmethod
from typing import Optional, List


class EmbeddingService(ABC):
    """嵌入服务接口"""
    
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文本"""
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """嵌入查询文本"""
        pass


class LLMService(ABC):
    """LLM服务接口"""
    
    @abstractmethod
    def generate(self, prompt: str, temperature: Optional[float] = None) -> str:
        """生成文本"""
        pass