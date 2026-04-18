# app/infrastructure/ai/llm.py
"""DeepSeek LLM实现"""

import requests
from typing import Optional
from ...config import settings
from .base import LLMService


class DeepSeekService(LLMService):
    """DeepSeek API服务"""
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured")
    
    def generate(self, prompt: str, temperature: Optional[float] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature or self.temperature
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']