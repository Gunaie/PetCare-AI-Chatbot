# app/infrastructure/database/chroma_repository.py
"""ChromaDB仓储实现"""

import os
from typing import List, Dict, Any
import chromadb
from app.config import settings
from app.domain.models import TextChunk, Document
from app.domain.repositories import VectorRepository


class ChromaRepository(VectorRepository):
    """ChromaDB向量仓储实现"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        try:
            self.collection = self.client.get_collection("documents")
        except:
            self.collection = self.client.create_collection(
                "documents", 
                embedding_function=None  # 我们手动管理嵌入
            )
    
    def add_chunks(self, chunks: List[TextChunk]) -> None:
        """添加文本块"""
        if not chunks:
            return
        
        ids = [c.id for c in chunks]
        documents = [c.content for c in chunks]
        embeddings = [c.embedding for c in chunks if c.embedding]
        metadatas = [
            {
                "document_id": c.document_id,
                "filename": c.metadata.get("filename", ""),
                "index": c.index
            } 
            for c in chunks
        ]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[TextChunk]:
        """向量搜索"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        chunks = []
        for i, doc in enumerate(results['documents'][0]):
            meta = results['metadatas'][0][i] if results['metadatas'] else {}
            chunks.append(TextChunk(
                id=f"result_{i}",
                content=doc,
                embedding=None,
                metadata=meta,
                document_id=meta.get("document_id", "") if meta else ""
            ))
        return chunks
    
    def exists(self, filename: str) -> bool:
        """检查文件是否存在"""
        try:
            all_data = self.collection.get()
            if not all_data or not all_data['metadatas']:
                return False
            
            for meta in all_data['metadatas']:
                if meta and meta.get('filename') == filename:
                    return True
            return False
        except Exception:
            return False
    
    def list_documents(self) -> Dict[str, Any]:
        """列出文档统计"""
        try:
            data = self.collection.get()
            filenames = set()
            if data and data['metadatas']:
                for m in data['metadatas']:
                    if m and 'filename' in m:
                        filenames.add(m['filename'])
            
            return {
                "total_chunks": self.collection.count(),
                "files": list(filenames),
                "message": f"共 {self.collection.count()} 个片段，{len(filenames)} 个文件"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_document_chunks(self, document_id: str) -> List[TextChunk]:
        # 简化实现，实际需要按metadata过滤
        return []
    
    def delete_document(self, document_id: str) -> None:
        # 简化实现
        pass