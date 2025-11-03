"""
API endpoints for daily notes functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from ..database import get_db
from ..models import DailyNote, User
from ..schemas.daily_notes import DailyNoteCreate, DailyNoteUpdate, DailyNoteResponse
from .dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=DailyNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_daily_note(
    daily_note: DailyNoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update a daily note for a specific date

    If a daily note already exists for the given date, it will be updated.
    Otherwise, a new daily note will be created.

    Args:
        daily_note: Daily note creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created or updated daily note
    """
    # Check if daily note already exists for this date
    existing_note = (
        db.query(DailyNote)
        .filter(
            DailyNote.user_id == current_user.id,
            DailyNote.note_date == daily_note.note_date
        )
        .first()
    )

    if existing_note:
        # Update existing daily note
        existing_note.content = daily_note.content
        db.commit()
        db.refresh(existing_note)
        return existing_note
    else:
        # Create new daily note
        db_daily_note = DailyNote(
            user_id=current_user.id,
            note_date=daily_note.note_date,
            content=daily_note.content
        )

        db.add(db_daily_note)
        db.commit()
        db.refresh(db_daily_note)

        return db_daily_note


@router.get("/", response_model=List[DailyNoteResponse])
async def get_daily_notes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all daily notes for the authenticated user with pagination

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of user's daily notes, ordered by date (most recent first)
    """
    daily_notes = (
        db.query(DailyNote)
        .filter(DailyNote.user_id == current_user.id)
        .order_by(DailyNote.note_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return daily_notes


@router.get("/{note_date}", response_model=DailyNoteResponse)
async def get_daily_note_by_date(
    note_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a daily note for a specific date

    Args:
        note_date: Date for the daily note (YYYY-MM-DD)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Daily note for the specified date

    Raises:
        HTTPException: If daily note not found for the date
    """
    daily_note = (
        db.query(DailyNote)
        .filter(
            DailyNote.user_id == current_user.id,
            DailyNote.note_date == note_date
        )
        .first()
    )

    if not daily_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No daily note found for {note_date}"
        )

    return daily_note


@router.put("/{daily_note_id}", response_model=DailyNoteResponse)
async def update_daily_note(
    daily_note_id: UUID,
    daily_note_update: DailyNoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a daily note by ID

    Args:
        daily_note_id: Daily note UUID
        daily_note_update: Daily note update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated daily note

    Raises:
        HTTPException: If daily note not found or user doesn't have permission
    """
    daily_note = (
        db.query(DailyNote)
        .filter(DailyNote.id == daily_note_id, DailyNote.user_id == current_user.id)
        .first()
    )

    if not daily_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily note not found"
        )

    # Update content if provided
    if daily_note_update.content is not None:
        daily_note.content = daily_note_update.content

    db.commit()
    db.refresh(daily_note)

    return daily_note


@router.delete("/{daily_note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_daily_note(
    daily_note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a daily note

    Args:
        daily_note_id: Daily note UUID
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If daily note not found or user doesn't have permission
    """
    daily_note = (
        db.query(DailyNote)
        .filter(DailyNote.id == daily_note_id, DailyNote.user_id == current_user.id)
        .first()
    )

    if not daily_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily note not found"
        )

    db.delete(daily_note)
    db.commit()

    return None
