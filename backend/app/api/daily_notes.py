"""
API endpoints for daily notes functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from ..database import get_db
from ..models import DailyNote, DailyNoteLink, Note, User
from ..schemas.daily_notes import (
    DailyNoteCreate,
    DailyNoteUpdate,
    DailyNoteResponse,
    DailyNoteLinkResponse
)
from ..schemas.note import NoteResponse
from .dependencies import get_current_user

router = APIRouter()


def _get_linked_note_ids(daily_note: DailyNote, db: Session) -> List[UUID]:
    """Helper function to get linked note IDs for a daily note"""
    links = db.query(DailyNoteLink).filter(
        DailyNoteLink.daily_note_id == daily_note.id
    ).all()
    return [link.note_id for link in links]


def _build_response(daily_note: DailyNote, db: Session) -> DailyNoteResponse:
    """Helper to build DailyNoteResponse with linked notes"""
    response_data = {
        "id": daily_note.id,
        "user_id": daily_note.user_id,
        "note_date": daily_note.note_date,
        "content": daily_note.content,
        "created_at": daily_note.created_at,
        "updated_at": daily_note.updated_at,
        "linked_note_ids": _get_linked_note_ids(daily_note, db)
    }
    return DailyNoteResponse(**response_data)


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
        return _build_response(existing_note, db)
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

        return _build_response(db_daily_note, db)


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
    return [_build_response(dn, db) for dn in daily_notes]


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

    return _build_response(daily_note, db)


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

    return _build_response(daily_note, db)


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


@router.post("/{daily_note_id}/links/{note_id}", response_model=DailyNoteLinkResponse, status_code=status.HTTP_201_CREATED)
async def link_note_to_daily_note(
    daily_note_id: UUID,
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Link a note to a daily note

    Args:
        daily_note_id: Daily note UUID
        note_id: Note UUID to link
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created link

    Raises:
        HTTPException: If daily note or note not found, or user doesn't have permission
    """
    # Verify daily note exists and belongs to user
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

    # Verify note exists and belongs to user
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

    # Check if link already exists
    existing_link = (
        db.query(DailyNoteLink)
        .filter(
            DailyNoteLink.daily_note_id == daily_note_id,
            DailyNoteLink.note_id == note_id
        )
        .first()
    )

    if existing_link:
        return existing_link

    # Create new link
    link = DailyNoteLink(
        daily_note_id=daily_note_id,
        note_id=note_id
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link


@router.get("/{daily_note_id}/linked-notes", response_model=List[NoteResponse])
async def get_linked_notes(
    daily_note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all notes linked to a daily note

    Args:
        daily_note_id: Daily note UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of linked notes

    Raises:
        HTTPException: If daily note not found or user doesn't have permission
    """
    # Verify daily note exists and belongs to user
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

    # Get all linked notes
    links = (
        db.query(DailyNoteLink)
        .filter(DailyNoteLink.daily_note_id == daily_note_id)
        .all()
    )

    note_ids = [link.note_id for link in links]

    notes = (
        db.query(Note)
        .filter(Note.id.in_(note_ids))
        .all()
    )

    return notes


@router.delete("/{daily_note_id}/links/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_note_from_daily_note(
    daily_note_id: UUID,
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlink a note from a daily note

    Args:
        daily_note_id: Daily note UUID
        note_id: Note UUID to unlink
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If daily note, note, or link not found
    """
    # Verify daily note exists and belongs to user
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

    # Find and delete the link
    link = (
        db.query(DailyNoteLink)
        .filter(
            DailyNoteLink.daily_note_id == daily_note_id,
            DailyNoteLink.note_id == note_id
        )
        .first()
    )

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )

    db.delete(link)
    db.commit()

    return None


@router.post("/link-to-today/{note_id}", response_model=DailyNoteLinkResponse, status_code=status.HTTP_201_CREATED)
async def link_note_to_today(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Link a note to today's daily note (creates today's daily note if it doesn't exist)

    Args:
        note_id: Note UUID to link
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created link

    Raises:
        HTTPException: If note not found or user doesn't have permission
    """
    from datetime import date as date_class

    # Verify note exists and belongs to user
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

    # Get or create today's daily note
    today = date_class.today()
    daily_note = (
        db.query(DailyNote)
        .filter(
            DailyNote.user_id == current_user.id,
            DailyNote.note_date == today
        )
        .first()
    )

    if not daily_note:
        # Create today's daily note
        daily_note = DailyNote(
            user_id=current_user.id,
            note_date=today,
            content=""
        )
        db.add(daily_note)
        db.commit()
        db.refresh(daily_note)

    # Check if link already exists
    existing_link = (
        db.query(DailyNoteLink)
        .filter(
            DailyNoteLink.daily_note_id == daily_note.id,
            DailyNoteLink.note_id == note_id
        )
        .first()
    )

    if existing_link:
        return existing_link

    # Create new link
    link = DailyNoteLink(
        daily_note_id=daily_note.id,
        note_id=note_id
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link
