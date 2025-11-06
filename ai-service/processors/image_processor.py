"""
Image Processor - OCR and visual analysis
Supports: Images (jpg, png, gif, etc.)
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import base64

from .base import BaseProcessor, ProcessingResult, ProcessorError, ProcessorProvider
from services.llm_service import get_llm_service
from config import settings


class ImageProcessor(BaseProcessor):
    """
    Image processor with OCR and visual understanding

    Current implementation:
    - OCR: Tesseract (local, free)
    - Visual analysis: Gemini Vision (free tier)
    - Document detection: Invoice, receipt, form recognition

    Future support:
    - Local vision models
    - Advanced OCR engines
    """

    SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff']

    def __init__(self, provider: ProcessorProvider = ProcessorProvider.GEMINI_API):
        """Initialize image processor"""
        super().__init__(provider)
        self.llm = get_llm_service()

    def get_supported_formats(self) -> List[str]:
        """Get supported image formats"""
        return self.SUPPORTED_FORMATS

    def validate_file(self, file_path: str) -> bool:
        """Validate image file"""
        path = Path(file_path)
        if not path.exists():
            return False

        extension = path.suffix.lstrip('.').lower()
        return extension in self.SUPPORTED_FORMATS

    async def process(
        self,
        file_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """
        Process image file with OCR and visual analysis

        Args:
            file_path: Path to image file
            options: Optional parameters:
                - ocr_only: Skip visual analysis, only OCR
                - detect_document_type: Try to identify document type

        Returns:
            ProcessingResult with OCR text and visual analysis
        """
        try:
            options = options or {}

            # Validate file
            if not self.validate_file(file_path):
                raise ProcessorError(f"Invalid or unsupported image: {file_path}")

            # Perform OCR
            ocr_text = await self._perform_ocr(file_path, options)

            # If OCR found no text, still try visual analysis
            if not ocr_text.strip() or not options.get('ocr_only', False):
                # Visual analysis with Gemini Vision
                visual_analysis = await self._analyze_image_with_vision(file_path, ocr_text, options)
            else:
                visual_analysis = {
                    "description": "Image contains text",
                    "document_type": "text_document",
                }

            # Combine OCR text and visual analysis
            combined_text = ocr_text
            if visual_analysis.get("description"):
                combined_text = f"{ocr_text}\n\n[Image Description: {visual_analysis.get('description')}]"

            # Analyze content for tasks and suggestions
            analysis = await self.llm.analyze_content(combined_text, "image with text") if combined_text.strip() else {}

            # Extract invoice details if this is an invoice/receipt image
            invoice_data = None
            document_type = visual_analysis.get("document_type", "").lower()
            if any(keyword in document_type for keyword in ['invoice', 'receipt', 'bill', 'payment']):
                if ocr_text.strip():  # Only extract if we have OCR text
                    invoice_data = await self.llm.extract_invoice_details(ocr_text)

            return ProcessingResult(
                success=True,
                raw_text=ocr_text if ocr_text.strip() else visual_analysis.get("description", ""),
                summary=analysis.get("summary") or visual_analysis.get("description", ""),
                key_points=self._extract_key_points(ocr_text, visual_analysis),
                extracted_tasks=analysis.get("tasks", []),
                metadata={
                    "provider": self.provider.value,
                    "ocr_engine": "tesseract",
                    "vision_model": settings.gemini_vision_model,
                    "document_type": visual_analysis.get("document_type"),
                    "has_text": bool(ocr_text.strip()),
                    "word_count": len(ocr_text.split()) if ocr_text else 0,
                    "visual_elements": visual_analysis.get("elements", []),
                    "invoice_details": invoice_data,
                    "is_resource": analysis.get("is_resource", False),
                    "suggested_projects": analysis.get("projects", []),
                    "suggested_areas": analysis.get("areas", []),
                },
                confidence_score=analysis.get("confidence", 0.75),
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                error=f"Image processing failed: {str(e)}"
            )

    async def _perform_ocr(
        self,
        image_path: str,
        options: Dict[str, Any]
    ) -> str:
        """
        Perform OCR on image using Tesseract

        Args:
            image_path: Path to image
            options: OCR options

        Returns:
            Extracted text
        """
        try:
            import pytesseract
            from PIL import Image

            # Open image
            image = Image.open(image_path)

            # Perform OCR
            text = pytesseract.image_to_string(
                image,
                lang=options.get('language', settings.tesseract_lang),
                config=f'--dpi {settings.ocr_dpi}'
            )

            return text.strip()

        except ImportError:
            raise ProcessorError(
                "pytesseract not installed. Install with: pip install pytesseract\n"
                "Also ensure tesseract-ocr is installed on system"
            )
        except Exception as e:
            raise ProcessorError(f"OCR failed: {str(e)}")

    async def _analyze_image_with_vision(
        self,
        image_path: str,
        ocr_text: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze image using Gemini Vision

        Args:
            image_path: Path to image
            ocr_text: Already extracted OCR text (for context)
            options: Analysis options

        Returns:
            Dictionary with visual analysis results
        """
        if self.provider != ProcessorProvider.GEMINI_API:
            # Future: Support other vision APIs
            return {"description": "Visual analysis not available for this provider"}

        try:
            import google.generativeai as genai
            from PIL import Image

            # Configure Gemini
            genai.configure(api_key=settings.google_api_key)
            model = genai.GenerativeModel(settings.gemini_vision_model)

            # Open image
            image = Image.open(image_path)

            # Create prompt
            prompt = """Analyze this image and provide:

1. A brief description of what you see
2. The type of document/image (e.g., invoice, receipt, screenshot, diagram, photo, etc.)
3. Key visual elements or information
4. If it's a document, identify any important fields or data

Respond in JSON format:
{
    "description": "Brief description of the image",
    "document_type": "invoice|receipt|screenshot|diagram|photo|form|other",
    "elements": ["key element 1", "key element 2"],
    "important_info": ["any dates, amounts, or critical data"]
}"""

            if ocr_text:
                prompt += f"\n\nOCR Text already extracted:\n{ocr_text[:500]}"

            # Generate response
            response = model.generate_content([prompt, image])

            # Parse JSON response
            import json
            result_text = response.text

            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)
            return result

        except Exception as e:
            print(f"Vision analysis failed: {e}")
            return {
                "description": "Visual analysis unavailable",
                "document_type": "unknown",
                "elements": [],
            }

    def _extract_key_points(
        self,
        ocr_text: str,
        visual_analysis: Dict[str, Any]
    ) -> List[str]:
        """Extract key points from OCR text and visual analysis"""
        key_points = []

        # Add important info from visual analysis
        if visual_analysis.get("important_info"):
            key_points.extend(visual_analysis["important_info"][:3])

        # Add visual elements
        if visual_analysis.get("elements"):
            key_points.extend(visual_analysis["elements"][:2])

        # Add first few lines of OCR if available
        if ocr_text:
            lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
            key_points.extend(lines[:3])

        return key_points[:5]  # Return up to 5 key points
