"""
Main FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from .config import settings
from .database import init_db
from . import models  # Import models to register them with SQLAlchemy

# Import routers
from .api import capture
# from .api import auth, notes, daily_notes, media, para, links, chat

app = FastAPI(
    title=settings.app_name,
    description="Universal Capture & Relational PKM Assistant",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Debug middleware to log CORS requests
@app.middleware("http")
async def log_cors_requests(request: Request, call_next):
    """Log CORS-related information for debugging"""
    origin = request.headers.get("origin")
    if request.method == "OPTIONS":
        print(f"🔍 CORS Preflight: {request.method} {request.url.path}")
        print(f"   Origin: {origin}")
        print(f"   Allowed Origins: {settings.cors_origins}")

    response = await call_next(request)
    return response

# CORS middleware - must be added AFTER custom middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Initialize database tables
    init_db()
    print(f"🚀 {settings.app_name} backend starting...")
    print(f"📝 Environment: {settings.environment}")
    print(f"🔗 API Documentation: http://{settings.backend_host}:{settings.backend_port}/docs")
    print(f"🌐 CORS Origins: {settings.cors_origins}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(f"👋 {settings.app_name} backend shutting down...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Aura API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.environment
    }


# Include API routers
app.include_router(capture.router, prefix="/api/capture", tags=["Capture"])
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(notes.router, prefix="/api/notes", tags=["Notes"])
# app.include_router(daily_notes.router, prefix="/api/daily", tags=["Daily Notes"])
# app.include_router(media.router, prefix="/api/media", tags=["Media"])
# app.include_router(para.router, prefix="/api/para", tags=["PARA"])
# app.include_router(links.router, prefix="/api/links", tags=["Links"])
# app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
