# app/services/document_service.py
"""文档处理服务：协调PDF解析、分块、嵌入"""

from typing import List
from app.config import settings
from app.domain.models import Document, TextChunk
from app.infrastructure.document.pdf_processor import PDFProcessor
from app.infrastructure.ai.embeddings import LocalEmbeddingService


class DocumentService:
    """文档处理服务"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.embedder = LocalEmbeddingService()
        self.text_splitter = None
        try:
            from ...infrastructure.document.text_utils import TextSplitter
            self.text_splitter = TextSplitter()
        except ImportError:
            pass
    
    def process_file(self, file_path: str) -> tuple[Document, List[TextChunk]]:
        """
        处理文件：解析 → 清理 → 分块 → 嵌入
        返回 (文档对象, 文本块列表)
        """
        # 1. 解析文档
        if file_path.endswith('.pdf'):
            doc = self.pdf_processor.process(file_path)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc = Document(content=content, source_path=file_path)
        else:
            raise ValueError("不支持的文件格式")
        
        # 2. 分块
        if self.text_splitter:
            chunks_text = self.text_splitter.split(doc.content)
        else:
            # 简单分块
            chunks_text = [doc.content[i:i+800] for i in range(0, len(doc.content), 700)]
            chunks_text = [c for c in chunks_text if len(c) > 50]
        
        # 3. 生成嵌入
        embeddings = self.embedder.embed(chunks_text)
        
        # 4. 构建TextChunk对象
        chunks = []
        for i, (text, emb) in enumerate(zip(chunks_text, embeddings)):
            chunks.append(TextChunk(
                document_id=doc.id,
                content=text,
                embedding=emb,
                index=i,
                metadata={"filename": doc.source_path.split('/')[-1]}
            ))
        
        return doc, chunks