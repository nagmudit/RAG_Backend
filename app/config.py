import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "")
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Mistral model configurations
    mistral_llm_model: str = "mistral-large-latest"
    mistral_embed_model: str = "mistral-embed"
    
    # FAISS configuration
    faiss_dimension: int = 1024  # Mistral embedding dimension
    
    # Retrieval configuration
    top_k_documents: int = 5
    
    # Rate limiting configuration
    llm_min_request_interval: float = 2.0  # Minimum seconds between LLM requests
    llm_base_delay: float = 5.0  # Base delay for LLM rate limiting
    llm_max_retries: int = 3  # Maximum retries for LLM requests
    
    embedding_min_request_interval: float = 1.0  # Minimum seconds between embedding requests
    embedding_max_retries: int = 2  # Maximum retries for embedding requests
    embedding_batch_size: int = 20  # Batch size for embedding requests
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def validate_settings():
    """Validate that required settings are present."""
    if not settings.mistral_api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is required")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(settings.faiss_index_path), exist_ok=True)
    
    return True
