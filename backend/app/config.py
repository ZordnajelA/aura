"""
Configuration management for Aura backend
Uses pydantic-settings for environment variable validation
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Application
    app_name: str = "Aura"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://aura_user:aura_password@localhost:5432/aura_db"

    # Backend API
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    # Default CORS origins for development - override via BACKEND_CORS_ORIGINS env var
    backend_cors_origins: str = "http://localhost:3000,http://localhost:5173,http://192.168.50.201:3000,http://docker-1:3000"

    # AI Service
    ai_service_url: str = "http://localhost:8001"

    # Authentication
    jwt_secret_key: str = "your-super-secret-jwt-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # AI API Keys (provide at least one)
    google_api_key: str | None = None       # Primary: Gemini API
    openai_api_key: str | None = None       # Optional: OpenAI
    anthropic_api_key: str | None = None    # Optional: Anthropic
    default_llm_provider: str = "gemini"    # Options: gemini, openai, anthropic

    # Media Processing
    upload_dir: str = "/app/uploads"
    max_upload_size_mb: int = 100
    allowed_extensions: str = "jpg,jpeg,png,gif,pdf,docx,txt,mp3,wav,m4a,mp4,webm"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Logging
    log_level: str = "INFO"

    # Feature Flags
    enable_audio_processing: bool = True
    enable_video_processing: bool = True
    enable_ocr: bool = True
    enable_web_scraping: bool = True

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.backend_cors_origins.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions from comma-separated string"""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]


# Global settings instance
settings = Settings()
