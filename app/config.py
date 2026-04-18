"""配置管理：集中管理所有环境变量和配置项"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # 应用配置
    app_name: str = "PetCare AI"
    debug: bool = Field(default=False, description="调试模式")
    
    # 路径配置
    data_dir: str = Field(default="./data", description="上传文件存储目录")
    chroma_persist_dir: str = Field(default="./chroma_db", description="向量数据库路径")
    
    # AI模型配置
    embedding_model: str = Field(default="BAAI/bge-m3", description="嵌入模型名称")
    hf_endpoint: str = Field(default="https://hf-mirror.com", description="HuggingFace镜像")
    
    # LLM配置
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API密钥")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", description="DeepSeek基础URL")
    llm_model: str = Field(default="deepseek-chat", description="LLM模型名称")
    llm_temperature: float = Field(default=0.7, ge=0, le=2)
    
    # OCR配置
    ocr_engine: str = Field(default="paddle", description="OCR引擎: paddle/tesseract")
    ocr_lang: str = Field(default="ch", description="OCR语言")
    
    # 文本处理配置
    chunk_size: int = Field(default=800, ge=100, le=2000)
    chunk_overlap: int = Field(default=100, ge=0, le=500)
    min_chunk_length: int = Field(default=50, description="最小分块长度")


settings = Settings()