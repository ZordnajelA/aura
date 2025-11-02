"""
Pydantic schemas for capture functionality
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class CaptureType(str, Enum):
    """Types of captures"""
    TEXT = "text"
    LINK = "link"
    FILE = "file"


class CaptureCreate(BaseModel):
    """Schema for creating a capture"""
    type: CaptureType = Field(..., description="Type of capture")
    content: Optional[str] = Field(None, description="Text content or link URL")
    file_name: Optional[str] = Field(None, description="Original file name")


class CaptureResponse(BaseModel):
    """Schema for capture response"""
    id: int
    type: CaptureType
    content: Optional[str]
    file_path: Optional[str]
    file_name: Optional[str]
    file_type: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
