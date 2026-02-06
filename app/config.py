from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    google_api_key: str = ""
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "Adam"  # Default voice
    
    # CORS
    frontend_url: str = "http://localhost:5173"
    
    # Rate Limiting
    rate_limit_per_day: int = 10
    
    # Chroma DB
    chroma_persist_dir: str = "./chroma_db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
