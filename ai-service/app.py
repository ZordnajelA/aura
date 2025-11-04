"""
AI Processing Service for Aura
Handles transcription, OCR, summarization, and AI analysis
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

from processors import (
    AudioProcessor,
    ImageProcessor,
    DocumentProcessor,
    TextClassifier,
    ProcessorProvider,
)
from services.llm_service import get_llm_service
from services.rate_limiter import get_rate_limiter
from config import settings

load_dotenv()

app = FastAPI(
    title="Aura AI Service",
    description="AI processing microservice for media analysis and content extraction",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProcessingRequest(BaseModel):
    """Request model for processing tasks"""
    file_path: str
    options: Optional[Dict[str, Any]] = None


class ClassifyRequest(BaseModel):
    """Request model for text classification"""
    text: str
    context: Optional[str] = None
    user_areas: Optional[List[str]] = None
    user_projects: Optional[List[str]] = None


class ChatRequest(BaseModel):
    """Request model for chat"""
    message: str
    session_id: Optional[str] = None
    context_notes: Optional[List[str]] = None


class ProcessingResponse(BaseModel):
    """Response model for processing results"""
    success: bool
    raw_text: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    extracted_tasks: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aura AI Service",
        "version": "1.0.0",
        "status": "running",
        "providers": {
            "default": settings.default_llm_provider,
            "gemini_model": settings.gemini_model,
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    rate_limiter = get_rate_limiter(settings.default_llm_provider)
    usage_stats = rate_limiter.get_usage_stats()

    return {
        "status": "healthy",
        "provider": settings.default_llm_provider,
        "rate_limits": usage_stats,
    }


@app.post("/process/audio", response_model=ProcessingResponse)
async def process_audio(request: ProcessingRequest):
    """
    Process audio file: transcribe and analyze

    Args:
        request: ProcessingRequest with file_path and options

    Returns:
        ProcessingResponse with transcription and analysis
    """
    try:
        if not settings.enable_audio_processing:
            raise HTTPException(
                status_code=503,
                detail="Audio processing is disabled"
            )

        processor = AudioProcessor(ProcessorProvider.OPENAI_API)
        result = await processor.process(request.file_path, request.options)

        return ProcessingResponse(**result.to_dict())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/video", response_model=ProcessingResponse)
async def process_video(request: ProcessingRequest):
    """
    Process video file: extract audio, transcribe and analyze
    Also handles YouTube URLs

    Args:
        request: ProcessingRequest with file_path (or YouTube URL) and options

    Returns:
        ProcessingResponse with transcription and analysis
    """
    try:
        if not settings.enable_video_processing:
            raise HTTPException(
                status_code=503,
                detail="Video processing is disabled"
            )

        processor = AudioProcessor(ProcessorProvider.OPENAI_API)
        result = await processor.process(request.file_path, request.options)

        return ProcessingResponse(**result.to_dict())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/image", response_model=ProcessingResponse)
async def process_image(request: ProcessingRequest):
    """
    Process image file: OCR and visual analysis

    Args:
        request: ProcessingRequest with file_path and options

    Returns:
        ProcessingResponse with OCR text and analysis
    """
    try:
        if not settings.enable_ocr:
            raise HTTPException(
                status_code=503,
                detail="Image processing is disabled"
            )

        processor = ImageProcessor(ProcessorProvider.GEMINI_API)
        result = await processor.process(request.file_path, request.options)

        return ProcessingResponse(**result.to_dict())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/document", response_model=ProcessingResponse)
async def process_document(request: ProcessingRequest):
    """
    Process document file: extract text and analyze
    Supports PDF, DOCX, TXT

    Args:
        request: ProcessingRequest with file_path and options

    Returns:
        ProcessingResponse with extracted text and analysis
    """
    try:
        processor = DocumentProcessor(ProcessorProvider.GEMINI_API)
        result = await processor.process(request.file_path, request.options)

        return ProcessingResponse(**result.to_dict())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify", response_model=ProcessingResponse)
async def classify_text(request: ClassifyRequest):
    """
    Classify text content and suggest PARA organization

    Args:
        request: ClassifyRequest with text and optional context

    Returns:
        ProcessingResponse with classification and suggestions
    """
    try:
        options = {
            "context": request.context,
            "user_areas": request.user_areas,
            "user_projects": request.user_projects,
        }

        classifier = TextClassifier(ProcessorProvider.GEMINI_API)
        result = await classifier.process(request.text, options)

        return ProcessingResponse(**result.to_dict())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat interface with context awareness

    Args:
        request: ChatRequest with message, session_id, and context_notes

    Returns:
        Chat response with suggestions
    """
    try:
        llm = get_llm_service()

        # Build context from notes if provided
        context = ""
        if request.context_notes:
            context = f"\nContext: User is asking about notes: {', '.join(request.context_notes)}"

        # Generate response
        prompt = f"{context}\n\nUser: {request.message}\n\nAssistant:"
        response = await llm.generate(prompt, max_tokens=500, temperature=0.7)

        return {
            "success": True,
            "message": response,
            "session_id": request.session_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
