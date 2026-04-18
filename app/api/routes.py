# app/api/routes.py
"""路由定义"""

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
import shutil
import os

from app.config import settings
from app.api.dependencies import get_rag_service  # 确保这一行存在
from app.api.schemas import UploadResponse, QueryResponse, DocumentListResponse
from app.services.rag_service import RAGService

# 确保数据目录存在
os.makedirs(settings.data_dir, exist_ok=True)

router = APIRouter()


@router.get("/")
def root():
    return {
        "message": f"{settings.app_name} 运行中",
        "docs": "/docs",
        "web": "/static/index.html"
    }


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    rag_service: RAGService = Depends(get_rag_service)
):
    """单文件上传"""
    file_path = os.path.join(settings.data_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    result = rag_service.add_document(file_path)
    return UploadResponse(**result)


@router.post("/upload-multiple")
async def upload_multiple(
    files: List[UploadFile] = File(...),
    rag_service: RAGService = Depends(get_rag_service)
):
    """多文件上传"""
    results = []
    success = skipped = error = 0
    
    for file in files:
        file_path = os.path.join(settings.data_dir, file.filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            result = rag_service.add_document(file_path)
            results.append(result)
            
            if result["status"] == "success":
                success += 1
            elif result["status"] == "skipped":
                skipped += 1
            else:
                error += 1
        except Exception as e:
            error += 1
            results.append({
                "status": "error",
                "message": str(e),
                "filename": file.filename
            })
    
    summary = f"上传完成：{success}个成功"
    if skipped > 0:
        summary += f"，{skipped}个已存在"
    if error > 0:
        summary += f"，{error}个失败"
    
    return {
        "summary": summary,
        "total": len(files),
        "success": success,
        "skipped": skipped,
        "error": error,
        "results": results
    }


@router.post("/query", response_model=QueryResponse)
async def query(
    question: str = Form(...),
    rag_service: RAGService = Depends(get_rag_service)
):
    """知识库查询"""
    result = rag_service.query(question)
    return QueryResponse(**result)


@router.get("/status", response_model=DocumentListResponse)
async def status(
    rag_service: RAGService = Depends(get_rag_service)
):
    """知识库状态"""
    result = rag_service.list_documents()
    return DocumentListResponse(**result)