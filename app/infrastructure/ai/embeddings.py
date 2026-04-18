# app/infrastructure/ai/embeddings.py
"""嵌入模型实现"""

import os
from typing import List
from sentence_transformers import SentenceTransformer
from ...config import settings
from .base import EmbeddingService


class LocalEmbeddingService(EmbeddingService):
    """本地嵌入模型服务（单例模式）"""
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            os.environ['HF_ENDPOINT'] = settings.hf_endpoint
        return cls._instance
    
    def _get_model(self):
        if self._model is None:
            self._model = SentenceTransformer(settings.embedding_model)
        return self._model
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        return self.embed([text])[0]