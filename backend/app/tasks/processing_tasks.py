"""
Celery tasks for async media processing
"""

import json
from datetime import datetime
from typing import Dict, Any
import httpx

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models import ProcessingJob, ProcessedContent, Media, Note, JobStatus, JobType, ContentType
from app.config import settings


@celery_app.task(bind=True, name="process_media")
def process_media_task(self, job_id: str):
    """
    Process media file asynchronously

    Args:
        job_id: UUID of the ProcessingJob
    """
    db = SessionLocal()

    try:
        # Get the job
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            raise Exception(f"Job {job_id} not found")

        # Update job status
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()

        # Get media and note info
        media = db.query(Media).filter(Media.id == job.media_id).first()
        note = db.query(Note).filter(Note.id == job.note_id).first()

        if not media:
            raise Exception("Media not found")

        # Build file path
        file_path = f"{settings.upload_dir}/{media.file_path}"

        # Determine processing endpoint based on job type
        endpoint_map = {
            JobType.AUDIO: "/process/audio",
            JobType.VIDEO: "/process/video",
            JobType.IMAGE: "/process/image",
            JobType.DOCUMENT: "/process/document",
        }

        endpoint = endpoint_map.get(job.job_type)
        if not endpoint:
            raise Exception(f"Unknown job type: {job.job_type}")

        # Call AI service
        ai_service_url = f"{settings.ai_service_url}{endpoint}"

        with httpx.Client(timeout=600.0) as client:  # 10 minute timeout
            response = client.post(
                ai_service_url,
                json={
                    "file_path": file_path,
                    "options": {}
                }
            )
            response.raise_for_status()
            result = response.json()

        if not result.get("success"):
            raise Exception(result.get("error", "Processing failed"))

        # Map content type from job type
        content_type_map = {
            JobType.AUDIO: ContentType.TRANSCRIPTION,
            JobType.VIDEO: ContentType.TRANSCRIPTION,
            JobType.IMAGE: ContentType.OCR,
            JobType.DOCUMENT: ContentType.DOCUMENT_TEXT,
        }

        # Store processed content
        processed_content = ProcessedContent(
            note_id=job.note_id,
            processing_job_id=job.id,
            content_type=content_type_map.get(job.job_type, ContentType.SUMMARY),
            raw_text=result.get("raw_text"),
            summary=result.get("summary"),
            key_points=json.dumps(result.get("key_points", [])),
            extracted_tasks=json.dumps(result.get("extracted_tasks", [])),
            processing_metadata=json.dumps(result.get("metadata", {})),
            confidence_score=int((result.get("confidence_score", 0.8) * 100)),
        )
        db.add(processed_content)

        # Update note content if empty
        if not note.content and result.get("raw_text"):
            note.content = result.get("raw_text")[:5000]  # Limit to 5000 chars

        # Update media as processed
        if media:
            media.is_processed = True

        # Update job as completed
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.completed_at = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "job_id": str(job.id),
            "processed_content_id": str(processed_content.id),
        }

    except Exception as e:
        # Mark job as failed
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()

        raise

    finally:
        db.close()


@celery_app.task(bind=True, name="classify_text")
def classify_text_task(self, note_id: str, user_areas: list = None, user_projects: list = None):
    """
    Classify text content asynchronously

    Args:
        note_id: UUID of the Note
        user_areas: List of user's areas (for context)
        user_projects: List of user's projects (for context)
    """
    db = SessionLocal()

    try:
        # Get the note
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise Exception(f"Note {note_id} not found")

        if not note.content:
            return {"success": False, "error": "Note has no content to classify"}

        # Call AI service
        ai_service_url = f"{settings.ai_service_url}/classify"

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                ai_service_url,
                json={
                    "text": note.content,
                    "user_areas": user_areas or [],
                    "user_projects": user_projects or [],
                }
            )
            response.raise_for_status()
            result = response.json()

        if not result.get("success"):
            raise Exception(result.get("error", "Classification failed"))

        # Store classification result
        from app.models import TextClassification, ClassificationType, Priority

        # Parse classification type
        classification_type_str = result.get("metadata", {}).get("classification_type", "other")
        try:
            classification_type = ClassificationType[classification_type_str.upper()]
        except KeyError:
            classification_type = ClassificationType.OTHER

        # Parse priority
        priority_str = result.get("metadata", {}).get("priority")
        priority = None
        if priority_str:
            try:
                priority = Priority[priority_str.upper()]
            except KeyError:
                pass

        classification = TextClassification(
            note_id=note.id,
            classification_type=classification_type,
            confidence=int((result.get("confidence_score", 0.8) * 100)),
            suggested_area=result.get("metadata", {}).get("suggested_area"),
            suggested_project=result.get("metadata", {}).get("suggested_project"),
            is_actionable=result.get("metadata", {}).get("is_actionable", False),
            priority=priority,
        )
        db.add(classification)
        db.commit()

        return {
            "success": True,
            "note_id": str(note.id),
            "classification_id": str(classification.id),
            "classification_type": classification_type.value,
        }

    except Exception as e:
        raise

    finally:
        db.close()
