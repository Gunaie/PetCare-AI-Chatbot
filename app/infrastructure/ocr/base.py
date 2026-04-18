# app/infrastructure/ocr/base.py
"""OCR接口"""

from abc import ABC, abstractmethod
from typing import List
from PIL import Image


class OCREngine(ABC):
    """OCR引擎接口"""
    
    @abstractmethod
    def recognize(self, image: Image.Image) -> List[str]:
        """识别图片中的文字，返回文本行列表"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """引擎是否可用"""
        pass