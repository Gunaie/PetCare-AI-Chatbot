# app/services/rag_service.py
"""RAG核心服务：协调检索和生成"""

from app.infrastructure.database.chroma_repository import ChromaRepository
from app.infrastructure.ai.embeddings import LocalEmbeddingService
from app.infrastructure.ai.llm import DeepSeekService
from typing import List, Dict, Any
import os
from app.config import settings
from app.domain.repositories import VectorRepository
from app.infrastructure.database.chroma_repository import ChromaRepository
from app.infrastructure.ai.embeddings import LocalEmbeddingService
from app.infrastructure.ai.llm import DeepSeekService
from app.services.interfaces import RAGServiceInterface
from app.services.interfaces import RAGServiceInterface
from app.services.document_service import DocumentService
from app.config import settings


class RAGService(RAGServiceInterface):
    """RAG服务实现"""
    
    def __init__(
        self,
        vector_repo: VectorRepository = None,
        document_service: DocumentService = None,
        llm_service: DeepSeekService = None
    ):
        self.vector_repo = vector_repo or ChromaRepository()
        self.doc_service = document_service or DocumentService()
        self.llm = llm_service or DeepSeekService()
    
    def add_document(self, file_path: str) -> Dict[str, Any]:
        """添加文档到知识库"""
        filename = os.path.basename(file_path)
        
        # 检查重复
        if self.vector_repo.exists(filename):
            return {
                "status": "skipped",
                "message": f"文档 [{filename}] 已存在",
                "filename": filename
            }
        
        try:
            # 处理文档
            doc, chunks = self.doc_service.process_file(file_path)
            
            if not chunks:
                return {
                    "status": "error",
                    "message": "未能生成有效文本块",
                    "filename": filename
                }
            
            # 存储到向量库
            self.vector_repo.add_chunks(chunks)
            
            return {
                "status": "success",
                "message": f"成功添加 {len(chunks)} 个片段",
                "filename": filename,
                "chunk_count": len(chunks),
                "char_count": len(doc.content)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "filename": filename
            }
    
    def query(self, question: str) -> Dict[str, Any]:
        """RAG查询"""
        # 1. 嵌入查询
        query_embedding = self.doc_service.embedder.embed_query(question)
        
        # 2. 检索相关块
        chunks = self.vector_repo.search(query_embedding, top_k=5)
        
        disclaimer = "⚠️ 免责声明：以上信息仅供参考，宠物健康问题请务必咨询专业兽医。"
        
        if not chunks:
            return {
                "answer": f"知识库中没有相关内容\n\n{disclaimer}",
                "sources": []
            }
        
        # 3. 去重
        unique_chunks = []
        seen = set()
        for chunk in chunks:
            fingerprint = chunk.content[:100]
            if fingerprint not in seen:
                seen.add(fingerprint)
                unique_chunks.append(chunk)
                if len(unique_chunks) >= 3:
                    break
        
        # 4. 构建上下文
        context = "\n\n".join([c.content for c in unique_chunks])
        
        # 5. 生成提示词（强制添加末尾免责声明）
        prompt = f"""基于以下知识库内容回答问题：

【知识库内容】
{context}

【问题】
{question}

回答要求：
1. 简洁直接，给出具体答案，不要寒暄
2. 只回答用户问的问题，不要扩展无关内容
3. 基于知识库内容回答，不要编造
4. 如知识库无相关信息，回答"根据现有资料无法确定"

【强制要求 - 必须遵守】
你的回答必须严格按以下格式输出：
1. 首先给出问题的直接回答
2. 然后换行，单独输出以下免责声明（一字不差，不得省略）：

{disclaimer}

请严格按格式回答："""
        
        # 6. 调用LLM
        answer = self.llm.generate(prompt)
        
        # 7. 安全检查：确保有免责声明
        if disclaimer not in answer:
            answer = answer.strip() + "\n\n" + disclaimer
        
        # 8. 智能来源过滤：如果 LLM 明确表示无法确定，不显示来源
        uncertain_indicators = [
            "根据现有资料无法确定",
            "无法确定",
            "知识库中没有相关内容",
            "没有相关信息"
        ]
        
        is_uncertain = any(indicator in answer for indicator in uncertain_indicators)
        
        if is_uncertain:
            sources = []  # 不显示无关来源
        else:
            # 正常情况，格式化来源
            sources = []
            for i, chunk in enumerate(unique_chunks, 1):
                filename = chunk.metadata.get('filename', '未知文件')
                content = chunk.content[:150].replace('\n', ' ')
                sources.append(f"[{i}] 《{filename}》{content}...")
        
        return {
            "answer": answer,
            "sources": sources
        }
    
    def list_documents(self) -> Dict[str, Any]:
        return self.vector_repo.list_documents()