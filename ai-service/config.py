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

    # AI API Keys (provide at least one)
    google_api_key: str | None = None       # Primary: Gemini API
    openai_api_key: str | None = None       # Optional: OpenAI
    anthropic_api_key: str | None = None    # Optional: Anthropic

    # Model configuration
    default_llm_provider: str = "gemini"    # Options: gemini, openai, anthropic

    # Provider-specific models
    gemini_model: str = "gemini-2.0-flash-exp"  # Free tier: gemini-2.0-flash-exp, gemini-1.5-flash
    gemini_vision_model: str = "gemini-2.0-flash-exp"  # For image analysis
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Rate limiting (Gemini free tier: 10 RPM, 4000 RPD)
    gemini_rpm_limit: int = 10  # Requests per minute
    gemini_rpd_limit: int = 4000  # Requests per day
    openai_rpm_limit: int = 60
    anthropic_rpm_limit: int = 50

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
