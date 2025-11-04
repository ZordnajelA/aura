"""
Pydantic schemas for note functionality
"""

from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class NoteCreate(BaseModel):
    """Schema for creating a note"""
    title: Optional[str] = Field(None, max_length=500, description="Note title")
    content: Optional[str] = Field(None, description="Note content")
    note_type: str = Field("text", description="Type of note (text, audio, image, pdf, link, video)")


class NoteUpdate(BaseModel):
    """Schema for updating a note"""
    title: Optional[str] = Field(None, max_length=500, description="Note title")
    content: Optional[str] = Field(None, description="Note content")
    note_type: Optional[str] = Field(None, description="Type of note")


class MediaInfo(BaseModel):
    """Schema for media file information in note responses"""
    id: UUID
    file_path: str
    file_type: str
    file_size: Optional[int]
    mime_type: Optional[str]

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def url(self) -> str:
        """Compute URL from file_path"""
        return f"/uploads/{self.file_path}"


class NoteResponse(BaseModel):
    """Schema for note response"""
    id: UUID
    user_id: UUID
    title: Optional[str]
    content: Optional[str]
    note_type: str
    created_at: datetime
    updated_at: datetime
    media_files: Optional[List[MediaInfo]] = Field(default=None, description="Attached media files")

    model_config = {"from_attributes": True}


class NoteLinkCreate(BaseModel):
    """Schema for creating a link between notes"""
    source_note_id: UUID
    target_note_id: UUID
    relation_type: str = Field("related", description="Type of relationship (related, references, depends_on)")


class NoteLinkResponse(BaseModel):
    """Schema for note link response"""
    id: UUID
    source_note_id: UUID
    target_note_id: UUID
    relation_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
