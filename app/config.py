from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    google_api_key: str = ""
    
    # AWS Polly TTS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    polly_voice_id: str = "Matthew"  # Neural voice
    polly_engine: str = "neural"  # standard, neural, long-form, generative
    
    # CORS
    frontend_url: str = "http://localhost:5173"
    
    # Rate Limiting
    rate_limit_per_day: int = 10
    
    # Chroma DB
    chroma_persist_dir: str = "./chroma_db"
    
    # Private Knowledge Repository
    github_token: str = ""
    private_knowledge_repo: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars (e.g., legacy ElevenLabs settings)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
