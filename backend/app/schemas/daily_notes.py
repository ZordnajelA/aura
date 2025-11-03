"""
Pydantic schemas for daily notes functionality
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID


class DailyNoteCreate(BaseModel):
    """Schema for creating or updating a daily note"""
    note_date: date = Field(..., description="Date for the daily note")
    content: Optional[str] = Field(None, description="Daily note content")


class DailyNoteUpdate(BaseModel):
    """Schema for updating a daily note"""
    content: Optional[str] = Field(None, description="Daily note content")


class DailyNoteResponse(BaseModel):
    """Schema for daily note response"""
    id: UUID
    user_id: UUID
    note_date: date
    content: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DailyNoteLinkCreate(BaseModel):
    """Schema for linking a note to a daily note"""
    daily_note_id: UUID
    note_id: UUID


class DailyNoteLinkResponse(BaseModel):
    """Schema for daily note link response"""
    id: UUID
    daily_note_id: UUID
    note_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
