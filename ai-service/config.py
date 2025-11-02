"""
Configuration for AI Service
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AI Service settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # AI API Keys
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # Model configuration
    default_llm_provider: str = "openai"
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_model: str = "claude-3-sonnet-20240229"

    # Audio settings
    whisper_model: str = "base"
    audio_sample_rate: int = 16000

    # OCR settings
    tesseract_lang: str = "eng"
    ocr_dpi: int = 300

    # File paths
    upload_dir: str = "/app/uploads"
    models_dir: str = "/app/models"

    # Feature flags
    enable_audio_processing: bool = True
    enable_video_processing: bool = True
    enable_ocr: bool = True
    enable_web_scraping: bool = True


settings = Settings()
