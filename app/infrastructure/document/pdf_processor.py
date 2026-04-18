# app/infrastructure/document/pdf_processor.py
"""PDF处理：文字提取 + OCR"""

import fitz  # PyMuPDF
from typing import List, Optional
from PIL import Image
from io import BytesIO
from app.config import settings
from ...domain.models import Document
from .text_utils import TextCleaner
from ..ocr.base import OCREngine
from ..ocr.paddle import PaddleOCREngine


class PDFProcessor:
    """PDF处理器：协调文字提取和OCR"""
    
    def __init__(self, ocr_engine: Optional[OCREngine] = None):
        self.ocr = ocr_engine or PaddleOCREngine()
        self.cleaner = TextCleaner()
    
    def process(self, file_path: str) -> Document:
        """处理PDF文件，返回Document实体"""
        # 1. 尝试提取文字层
        text = self._extract_text_layer(file_path)
        
        # 2. 如果文字太少，使用OCR
        if len(text.strip()) < 50:
            text = self._ocr_pdf(file_path)
        
        # 3. 清理文本
        original_len = len(text)
        text = self.cleaner.clean(text)
        
        return Document(
            content=text,
            source_path=file_path,
            metadata={
                "original_length": original_len,
                "cleaned_length": len(text),
                "used_ocr": len(text.strip()) < 100
            }
        )
    
    def _extract_text_layer(self, file_path: str) -> str:
        """提取PDF文字层"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"文字提取失败: {e}")
            return ""
    
    def _ocr_pdf(self, file_path: str) -> str:
        """OCR识别PDF（逐页）"""
        if not self.ocr.is_available:
            print("OCR引擎不可用")
            return ""
        
        try:
            doc = fitz.open(file_path)
            all_text = []
            
            for page_num, page in enumerate(doc):
                # 渲染页面为图片
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                
                # 转为PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # OCR识别
                texts = self.ocr.recognize(img)
                if texts:
                    all_text.append(f"--- 第{page_num+1}页 ---\n" + "\n".join(texts))
            
            doc.close()
            return "\n\n".join(all_text)
            
        except Exception as e:
            print(f"OCR处理失败: {e}")
            return ""