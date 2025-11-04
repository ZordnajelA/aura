"""
API endpoints for notes functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import Note, User, Area, Project, Resource, AreaNoteLink, ProjectNoteLink, ResourceNoteLink
from ..schemas.note import NoteCreate, NoteUpdate, NoteResponse
from ..schemas.para import AreaResponse, ProjectResponse, ResourceResponse
from .dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new note for the authenticated user

    Args:
        note: Note creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created note
    """
    db_note = Note(
        user_id=current_user.id,
        title=note.title,
        content=note.content,
        note_type=note.note_type
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note


@router.get("/", response_model=List[NoteResponse])
async def get_notes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all notes for the authenticated user with pagination

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of user's notes
    """
    notes = (
        db.query(Note)
        .filter(Note.user_id == current_user.id)
        .order_by(Note.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific note by ID

    Args:
        note_id: Note UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Note details

    Raises:
        HTTPException: If note not found or user doesn't have permission
    """
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    note_update: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a note

    Args:
        note_id: Note UUID
        note_update: Note update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated note

    Raises:
        HTTPException: If note not found or user doesn't have permission
    """
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Update fields if provided
    if note_update.title is not None:
        note.title = note_update.title
    if note_update.content is not None:
        note.content = note_update.content
    if note_update.note_type is not None:
        note.note_type = note_update.note_type

    db.commit()
    db.refresh(note)

    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a note

    Args:
        note_id: Note UUID
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If note not found or user doesn't have permission
    """
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    db.delete(note)
    db.commit()

    return None


# ============================================================================
# NOTE PARA LINKS ENDPOINTS
# ============================================================================

@router.get("/{note_id}/areas", response_model=List[AreaResponse])
async def get_note_areas(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all areas linked to a specific note

    Args:
        note_id: Note UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of areas linked to the note
    """
    # Verify note exists and belongs to user
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    # Get all areas linked to this note
    areas = (
        db.query(Area)
        .join(AreaNoteLink, AreaNoteLink.area_id == Area.id)
        .filter(AreaNoteLink.note_id == note_id, Area.user_id == current_user.id)
        .all()
    )

    return areas


@router.get("/{note_id}/projects", response_model=List[ProjectResponse])
async def get_note_projects(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects linked to a specific note

    Args:
        note_id: Note UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of projects linked to the note
    """
    # Verify note exists and belongs to user
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    # Get all projects linked to this note
    projects = (
        db.query(Project)
        .join(ProjectNoteLink, ProjectNoteLink.project_id == Project.id)
        .filter(ProjectNoteLink.note_id == note_id, Project.user_id == current_user.id)
        .all()
    )

    return projects


@router.get("/{note_id}/resources", response_model=List[ResourceResponse])
async def get_note_resources(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all resources linked to a specific note

    Args:
        note_id: Note UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of resources linked to the note
    """
    # Verify note exists and belongs to user
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    # Get all resources linked to this note
    resources = (
        db.query(Resource)
        .join(ResourceNoteLink, ResourceNoteLink.resource_id == Resource.id)
        .filter(ResourceNoteLink.note_id == note_id, Resource.user_id == current_user.id)
        .all()
    )

    return resources
