# app/api/schemas.py
"""Pydantic模型（DTO）"""

from pydantic import BaseModel
from typing import List, Optional


class UploadResponse(BaseModel):
    """上传响应"""
    status: str
    message: str
    filename: str
    chunk_count: Optional[int] = None


class QueryRequest(BaseModel):
    """查询请求"""
    question: str


class QueryResponse(BaseModel):
    """查询响应"""
    answer: str
    sources: List[str]


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    total_chunks: int
    files: List[str]
    message: str