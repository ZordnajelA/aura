"""
AI Processors - Provider abstraction layer for different processing types
Supports API-based and local model implementations
"""

from .base import BaseProcessor, ProcessingResult, ProcessorError, ProcessorProvider
from .audio_processor import AudioProcessor
from .image_processor import ImageProcessor
from .document_processor import DocumentProcessor
from .text_classifier import TextClassifier

__all__ = [
    "BaseProcessor",
    "ProcessingResult",
    "ProcessorError",
    "ProcessorProvider",
    "AudioProcessor",
    "ImageProcessor",
    "DocumentProcessor",
    "TextClassifier",
]
