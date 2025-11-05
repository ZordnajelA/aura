"""
Base Processor - Abstract interface for all media processors
Allows for both API-based and local model implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class ProcessorProvider(str, Enum):
    """Provider types for processors"""
    GEMINI_API = "gemini_api"
    OPENAI_API = "openai_api"
    ANTHROPIC_API = "anthropic_api"
    LOCAL_WHISPER = "local_whisper"
    LOCAL_TESSERACT = "local_tesseract"
    LOCAL_LLM = "local_llm"


@dataclass
class ProcessingResult:
    """Standardized result from any processor"""
    success: bool
    raw_text: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    extracted_tasks: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "raw_text": self.raw_text,
            "summary": self.summary,
            "key_points": self.key_points or [],
            "extracted_tasks": self.extracted_tasks or [],
            "metadata": self.metadata or {},
            "confidence_score": self.confidence_score,
            "error": self.error,
        }


class ProcessorError(Exception):
    """Custom exception for processor errors"""
    pass


class BaseProcessor(ABC):
    """
    Abstract base class for all media processors

    This design allows for future extensibility:
    - Current: API-based processing (Gemini, OpenAI, Claude)
    - Future: Local model support (LocalWhisper, LocalLLM, etc.)
    """

    def __init__(self, provider: ProcessorProvider):
        """
        Initialize processor with a specific provider

        Args:
            provider: The provider implementation to use
        """
        self.provider = provider

    @abstractmethod
    async def process(
        self,
        file_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """
        Process a file and return structured results

        Args:
            file_path: Absolute path to the file to process
            options: Optional processing parameters

        Returns:
            ProcessingResult with extracted content and analysis

        Raises:
            ProcessorError: If processing fails
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats for this processor

        Returns:
            List of file extensions (e.g., ['mp3', 'wav', 'm4a'])
        """
        pass

    @abstractmethod
    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file is processable

        Args:
            file_path: Path to file to validate

        Returns:
            True if file is valid and can be processed
        """
        pass

    def get_provider_name(self) -> str:
        """Get the provider name"""
        return self.provider.value
