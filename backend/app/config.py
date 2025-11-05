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

    # Server Domain/Hostname Configuration
    # Set this to your server's hostname, IP address, or domain name
    # Examples: "localhost", "192.168.50.201", "docker-1", "yourdomain.com"
    server_domain: str = "localhost"

    # Frontend Port (used for constructing CORS origins)
    frontend_port: int = 3000

    # Backend API
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    # Optional: Override CORS origins completely. If not set, will be auto-generated from server_domain
    backend_cors_origins: str | None = None

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

    # Redis (for Celery task queue)
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379

    # Logging
    log_level: str = "INFO"

    # Feature Flags
    enable_audio_processing: bool = True
    enable_video_processing: bool = True
    enable_ocr: bool = True
    enable_web_scraping: bool = True

    @property
    def cors_origins(self) -> List[str]:
        """
        Generate CORS origins automatically based on server_domain,
        or use manually specified BACKEND_CORS_ORIGINS if provided
        """
        if self.backend_cors_origins:
            # Use manually specified origins
            return [origin.strip() for origin in self.backend_cors_origins.split(",")]

        # Auto-generate CORS origins based on server_domain
        origins = []

        # Always include localhost for local development
        origins.extend([
            "http://localhost:3000",
            "http://localhost:5173",  # Vite dev server default
        ])

        # Add the configured server domain if it's not localhost
        if self.server_domain not in ["localhost", "127.0.0.1"]:
            protocol = "https" if self.environment == "production" else "http"
            origins.append(f"{protocol}://{self.server_domain}:{self.frontend_port}")

            # Also add port 5173 for Vite dev server
            if self.environment == "development":
                origins.append(f"{protocol}://{self.server_domain}:5173")

        return origins

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions from comma-separated string"""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]


# Global settings instance
settings = Settings()
