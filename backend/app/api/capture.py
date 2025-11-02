"""
API endpoints for capture functionality
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from ..database import get_db
from ..models import Capture, CaptureType
from ..schemas import CaptureCreate, CaptureResponse
from ..config import settings

router = APIRouter()


@router.post("/text", response_model=CaptureResponse, status_code=201)
async def capture_text(
    capture: CaptureCreate,
    db: Session = Depends(get_db)
):
    """
    Capture text or link content
    """
    db_capture = Capture(
        type=capture.type,
        content=capture.content
    )

    db.add(db_capture)
    db.commit()
    db.refresh(db_capture)

    return db_capture


@router.post("/file", response_model=CaptureResponse, status_code=201)
async def capture_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and capture a file
    """
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.upload_dir, unique_filename)

    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create database record
    db_capture = Capture(
        type=CaptureType.FILE,
        file_path=file_path,
        file_name=file.filename,
        file_type=file.content_type
    )

    db.add(db_capture)
    db.commit()
    db.refresh(db_capture)

    return db_capture


@router.get("/", response_model=List[CaptureResponse])
async def get_captures(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all captures with pagination
    """
    captures = db.query(Capture).order_by(Capture.created_at.desc()).offset(skip).limit(limit).all()
    return captures


@router.get("/{capture_id}", response_model=CaptureResponse)
async def get_capture(
    capture_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific capture by ID
    """
    capture = db.query(Capture).filter(Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")
    return capture
