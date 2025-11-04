"""
Pydantic schemas for media functionality
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class MediaUploadResponse(BaseModel):
    """Schema for media upload response"""
    id: UUID
    note_id: UUID
    file_path: str
    file_type: str
    file_size: Optional[int]
    mime_type: Optional[str]
    is_processed: bool
    created_at: datetime
    url: str  # Public URL to access the file

    model_config = {"from_attributes": True}


class MediaResponse(BaseModel):
    """Schema for media response"""
    id: UUID
    note_id: UUID
    file_path: str
    file_type: str
    file_size: Optional[int]
    mime_type: Optional[str]
    is_processed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NoteWithMediaCreate(BaseModel):
    """Schema for creating a note with an uploaded file"""
    title: Optional[str] = Field(None, max_length=500, description="Note title")
    content: Optional[str] = Field(None, description="Note content")
    note_type: str = Field(..., description="Type of note (audio, image, pdf, video)")
