# app/domain/models.py
"""领域实体：定义核心业务数据结构"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


@dataclass
class Document:
    """文档实体"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    source_path: str = ""
    
    @property
    def is_scanned(self) -> bool:
        """判断是否为扫描件（通过内容长度启发式判断）"""
        return len(self.content) < 100 if self.content else False


@dataclass
class TextChunk:
    """文本块实体"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    content: str = ""
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    index: int = 0  # 在原文档中的顺序


@dataclass
class SearchResult:
    """搜索结果"""
    chunk: TextChunk
    score: float
    document_name: str = ""