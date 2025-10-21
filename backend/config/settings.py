from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    mistral_api_key: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str = "us-east-1"
    pinecone_api_key: str
    tavily_api_key: str 
    perplexity_api_key: str 
    

    # S3 Configuration
    s3_bucket_name: str = "research-paper-analysis"
    s3_raw_pdf_prefix: str = "raw_pdfs"
    s3_parsed_markdown_prefix: str = "parsed_markdown"
    s3_hash_index_prefix: str = "hash_index"
    
    # Chunking Configuration
    chunk_size: int = 1500  
    chunk_overlap: int = 200  
    
    # File Upload Configuration
    max_file_size_mb: int = 5
    
    # Bedrock Configuration
    bedrock_embedding_model: str = "amazon.titan-embed-text-v2:0"
    bedrock_chat_model: str 
    embedding_dimension: int = 1024
    
    # Pinecone Configuration
    pinecone_index_name: str = "aws-pdf-index"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()
