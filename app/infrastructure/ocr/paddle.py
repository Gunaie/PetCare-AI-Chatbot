# app/infrastructure/ocr/paddle.py
"""PaddleOCR实现"""

import numpy as np
from typing import List
from PIL import Image
from .base import OCREngine


class PaddleOCREngine(OCREngine):
    """PaddleOCR实现"""
    
    def __init__(self):
        self._ocr = None
        self._initialized = False
    
    def _init(self):
        if not self._initialized:
            try:
                from paddleocr import PaddleOCR
                self._ocr = PaddleOCR(
                    use_angle_cls=False,
                    lang='ch',
                    show_log=False,
                    use_gpu=False,
                    det_limit_side_len=960,
                    drop_score=0.3
                )
                self._initialized = True
            except Exception as e:
                print(f"PaddleOCR初始化失败: {e}")
                raise
    
    @property
    def is_available(self) -> bool:
        try:
            self._init()
            return True
        except:
            return False
    
    def recognize(self, image: Image.Image) -> List[str]:
        self._init()
        img_array = np.array(image)
        result = self._ocr.ocr(img_array, cls=False)
        
        texts = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    texts.append(line[1][0])
        return texts