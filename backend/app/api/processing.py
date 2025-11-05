"""
Processing API endpoints
Manages async AI processing jobs and results
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import json

from ..database import get_db
from ..models import (
    User,
    ProcessingJob,
    ProcessedContent,
    Media,
    Note,
    JobStatus,
    Area,
    Project,
)
from ..api.dependencies import get_current_user
from ..tasks.processing_tasks import process_media_task, classify_text_task
from pydantic import BaseModel


router = APIRouter()


class ProcessingJobResponse(BaseModel):
    """Response model for processing job"""
    id: str
    note_id: str
    media_id: Optional[str]
    job_type: str
    status: str
    progress: int
    error_message: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class ProcessedContentResponse(BaseModel):
    """Response model for processed content"""
    id: str
    note_id: str
    content_type: str
    raw_text: Optional[str]
    summary: Optional[str]
    key_points: List[str]
    extracted_tasks: List[str]
    metadata: dict
    confidence_score: Optional[int]
    created_at: str

    class Config:
        from_attributes = True


@router.post("/start/{media_id}")
async def start_processing(
    media_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger processing for a media file

    Returns:
        ProcessingJob details
    """
    # Get media
    media = db.query(Media).filter(
        Media.id == media_id
    ).join(Note).filter(
        Note.user_id == current_user.id
    ).first()

    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    if media.is_processed:
        raise HTTPException(status_code=400, detail="Media already processed")

    # Determine job type from file extension
    from ..models import JobType
    extension = media.file_type.lower()

    if extension in ['mp3', 'wav', 'm4a', 'aac', 'ogg', 'flac']:
        job_type = JobType.AUDIO
    # Video files not supported (requires heavy moviepy dependency)
    # For video processing, use YouTube URLs instead
    elif extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
        job_type = JobType.IMAGE
    elif extension in ['pdf', 'docx', 'doc', 'txt']:
        job_type = JobType.DOCUMENT
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}. For video processing, use YouTube URLs."
        )

    # Create processing job
    job = ProcessingJob(
        user_id=current_user.id,
        media_id=media.id,
        note_id=media.note_id,
        job_type=job_type,
        status=JobStatus.PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Queue Celery task
    process_media_task.delay(str(job.id))

    return {
        "success": True,
        "job_id": str(job.id),
        "status": job.status.value,
        "message": "Processing started",
    }


@router.get("/status/{job_id}", response_model=ProcessingJobResponse)
async def get_job_status(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a processing job

    Returns:
        ProcessingJob details
    """
    job = db.query(ProcessingJob).filter(
        ProcessingJob.id == job_id,
        ProcessingJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return ProcessingJobResponse(
        id=str(job.id),
        note_id=str(job.note_id),
        media_id=str(job.media_id) if job.media_id else None,
        job_type=job.job_type.value,
        status=job.status.value,
        progress=job.progress,
        error_message=job.error_message,
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        created_at=job.created_at.isoformat(),
    )


@router.get("/results/{note_id}", response_model=List[ProcessedContentResponse])
async def get_processing_results(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all processing results for a note

    Returns:
        List of ProcessedContent
    """
    # Verify note ownership
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Get all processed content
    contents = db.query(ProcessedContent).filter(
        ProcessedContent.note_id == note_id
    ).all()

    return [
        ProcessedContentResponse(
            id=str(content.id),
            note_id=str(content.note_id),
            content_type=content.content_type.value,
            raw_text=content.raw_text,
            summary=content.summary,
            key_points=json.loads(content.key_points) if content.key_points else [],
            extracted_tasks=json.loads(content.extracted_tasks) if content.extracted_tasks else [],
            metadata=json.loads(content.processing_metadata) if content.processing_metadata else {},
            confidence_score=content.confidence_score,
            created_at=content.created_at.isoformat(),
        )
        for content in contents
    ]


@router.delete("/{job_id}")
async def cancel_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a processing job (if still pending)

    Returns:
        Success message
    """
    job = db.query(ProcessingJob).filter(
        ProcessingJob.id == job_id,
        ProcessingJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.status.value}"
        )

    # Mark as failed (Celery tasks are hard to cancel)
    job.status = JobStatus.FAILED
    job.error_message = "Cancelled by user"
    db.commit()

    return {
        "success": True,
        "message": "Job cancelled",
    }


@router.post("/classify/{note_id}")
async def classify_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Classify a text note

    Returns:
        Task status
    """
    # Verify note ownership
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if not note.content:
        raise HTTPException(status_code=400, detail="Note has no content to classify")

    # Get user's areas and projects for context
    areas = db.query(Area).filter(Area.user_id == current_user.id).all()
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()

    user_areas = [area.name for area in areas]
    user_projects = [project.name for project in projects]

    # Queue classification task
    task = classify_text_task.delay(
        str(note_id),
        user_areas=user_areas,
        user_projects=user_projects
    )

    return {
        "success": True,
        "task_id": task.id,
        "message": "Classification started",
    }
