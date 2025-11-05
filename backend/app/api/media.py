"""
API endpoints for media file uploads and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import os
import uuid as uuid_lib
from pathlib import Path
import shutil

from ..database import get_db
from ..models import Media, Note, User
from ..schemas.media import MediaUploadResponse, MediaResponse
from ..schemas.note import NoteResponse
from .dependencies import get_current_user
from ..config import settings

router = APIRouter()


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename"""
    return Path(filename).suffix.lower()


def determine_note_type(mime_type: str, file_extension: str) -> str:
    """Determine note type based on MIME type and file extension"""
    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type == 'application/pdf' or file_extension == '.pdf':
        return 'pdf'
    else:
        return 'file'


def validate_file_extension(filename: str) -> bool:
    """Validate that the file extension is allowed"""
    extension = get_file_extension(filename).lstrip('.')
    return extension in settings.allowed_extensions_list


def validate_file_size(file_size: int) -> bool:
    """Validate that the file size is within limits"""
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


@router.post("/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_media_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a media file and create an associated note

    Args:
        file: The file to upload
        title: Optional title for the note (defaults to filename)
        content: Optional content/description for the note
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created media record with note information
    """
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.allowed_extensions}"
        )

    # Read file to check size
    file_content = await file.read()
    file_size = len(file_content)

    # Validate file size
    if not validate_file_size(file_size):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_upload_size_mb}MB"
        )

    # Reset file pointer after reading
    await file.seek(0)

    # Generate unique filename
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid_lib.uuid4()}{file_extension}"

    # Create user-specific upload directory
    user_upload_dir = Path(settings.upload_dir) / str(current_user.id)
    user_upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = user_upload_dir / unique_filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Determine note type
    note_type = determine_note_type(file.content_type or '', file_extension)

    # Create note
    db_note = Note(
        user_id=current_user.id,
        title=title or file.filename,
        content=content or f"Uploaded file: {file.filename}",
        note_type=note_type
    )
    db.add(db_note)
    db.flush()  # Get the note ID without committing

    # Create media record
    # Store relative path from upload_dir
    relative_path = f"{current_user.id}/{unique_filename}"

    db_media = Media(
        note_id=db_note.id,
        file_path=relative_path,
        file_type=file_extension.lstrip('.'),
        file_size=file_size,
        mime_type=file.content_type,
        is_processed=False
    )

    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    db.refresh(db_note)

    # Automatically trigger AI processing (Phase 2)
    from ..models import ProcessingJob, JobStatus, JobType
    from ..tasks.processing_tasks import process_media_task

    # Determine job type from file extension
    extension = file_extension.lstrip('.').lower()
    job_type = None

    if extension in ['mp3', 'wav', 'm4a', 'aac', 'ogg', 'flac']:
        job_type = JobType.AUDIO
    # Video files not supported (requires heavy moviepy dependency)
    # For video processing, use YouTube URLs instead
    elif extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
        job_type = JobType.IMAGE
    elif extension in ['pdf', 'docx', 'doc', 'txt']:
        job_type = JobType.DOCUMENT

    # Create processing job if file type is supported
    if job_type and (
        (job_type == JobType.AUDIO and settings.enable_audio_processing) or
        (job_type == JobType.IMAGE and settings.enable_ocr) or
        (job_type == JobType.DOCUMENT)
    ):
        processing_job = ProcessingJob(
            user_id=current_user.id,
            media_id=db_media.id,
            note_id=db_note.id,
            job_type=job_type,
            status=JobStatus.PENDING,
        )
        db.add(processing_job)
        db.commit()
        db.refresh(processing_job)

        # Queue Celery task for async processing
        process_media_task.delay(str(processing_job.id))

    # Generate public URL
    media_url = f"/uploads/{relative_path}"

    return MediaUploadResponse(
        id=db_media.id,
        note_id=db_media.note_id,
        file_path=db_media.file_path,
        file_type=db_media.file_type,
        file_size=db_media.file_size,
        mime_type=db_media.mime_type,
        is_processed=db_media.is_processed,
        created_at=db_media.created_at,
        url=media_url
    )


@router.get("/note/{note_id}", response_model=List[MediaResponse])
async def get_note_media(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all media files associated with a note

    Args:
        note_id: ID of the note
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of media records
    """
    # Verify note exists and belongs to user
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Get all media for this note
    media_files = db.query(Media).filter(Media.note_id == note_id).all()

    return media_files


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific media file record

    Args:
        media_id: ID of the media file
        current_user: Current authenticated user
        db: Database session

    Returns:
        Media record
    """
    # Get media and verify it belongs to user's note
    media = db.query(Media).join(Note).filter(
        Media.id == media_id,
        Note.user_id == current_user.id
    ).first()

    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )

    return media


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a media file and its database record

    Args:
        media_id: ID of the media file
        current_user: Current authenticated user
        db: Database session

    Returns:
        None (204 No Content)
    """
    # Get media and verify it belongs to user's note
    media = db.query(Media).join(Note).filter(
        Media.id == media_id,
        Note.user_id == current_user.id
    ).first()

    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )

    # Delete physical file
    file_path = Path(settings.upload_dir) / media.file_path
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Warning: Failed to delete physical file {file_path}: {str(e)}")

    # Delete database record
    db.delete(media)
    db.commit()

    return None
