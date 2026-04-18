# app/infrastructure/document/text_utils.py
"""文本处理工具：清理、分块"""

import re
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings


class TextCleaner:
    """文本清理器"""
    
    # 定义需要去除的模式
    PATTERNS = [
        (r'MSD手册\s*兽医手册\s*宠物主人版本', ''),  # 标题
        (r'作者[：:]\s*[^\n]+?(?=\n|$)', ''),  # 作者行
        (r'审阅?[者人][：:]\s*[^\n]+?(?=\n|$)', ''),  # 审阅者
        (r'审查/修订\d+年\d+月', ''),  # 日期
        (r'Copyright\s*©[^\n]+', ''),  # 版权
        (r'MSD\s*[©®]?\s*[^\n]*', ''),  # MSD标志
        (r'学院站猫诊所[^\n]*', ''),  # 机构
        (r'Laurie\s*H?ess[^\n]*', ''),  # 人名
        (r'兽医博士[^\n]*', ''),  # 头衔
        (r'DABVP[^\n]*', ''),  # 认证
        (r'---\s*第\d+页\s*---', ''),  # 页码
        (r'回口', ''),  # OCR错误
    ]
    
    @classmethod
    def clean(cls, text: str) -> str:
        if not text:
            return text
        
        cleaned = text
        for pattern, repl in cls.PATTERNS:
            cleaned = re.sub(pattern, repl, cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # 清理空白
        cleaned = re.sub(r'\n+', '\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        return cleaned.strip()


class TextSplitter:
    """智能文本分块器"""
    
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", "。", "，", " ", ""],
            length_function=len,
        )
    
    def split(self, text: str) -> List[str]:
        """分块并过滤太短的块"""
        chunks = self.splitter.split_text(text)
        return [c for c in chunks if len(c) >= settings.min_chunk_length]