"""
Pydantic schemas for PARA (Projects, Areas, Resources, Archives) functionality
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from uuid import UUID


# Area Schemas

class AreaCreate(BaseModel):
    """Schema for creating an area"""
    name: str = Field(..., max_length=255, description="Area name")
    description: Optional[str] = Field(None, description="Area description")
    icon: Optional[str] = Field(None, max_length=50, description="Icon name or emoji")
    display_order: int = Field(0, description="Display order")


class AreaUpdate(BaseModel):
    """Schema for updating an area"""
    name: Optional[str] = Field(None, max_length=255, description="Area name")
    description: Optional[str] = Field(None, description="Area description")
    icon: Optional[str] = Field(None, max_length=50, description="Icon name or emoji")
    display_order: Optional[int] = Field(None, description="Display order")


class AreaResponse(BaseModel):
    """Schema for area response"""
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    icon: Optional[str]
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Project Schemas

class ProjectCreate(BaseModel):
    """Schema for creating a project"""
    name: str = Field(..., max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    area_id: Optional[UUID] = Field(None, description="Associated area ID")
    status: str = Field("active", description="Project status (active, completed, archived)")
    due_date: Optional[date] = Field(None, description="Project due date")


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    area_id: Optional[UUID] = Field(None, description="Associated area ID")
    status: Optional[str] = Field(None, description="Project status")
    due_date: Optional[date] = Field(None, description="Project due date")


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: UUID
    user_id: UUID
    area_id: Optional[UUID]
    name: str
    description: Optional[str]
    status: str
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Resource Schemas

class ResourceCreate(BaseModel):
    """Schema for creating a resource"""
    title: str = Field(..., max_length=500, description="Resource title")
    content: Optional[str] = Field(None, description="Resource content")
    area_id: Optional[UUID] = Field(None, description="Associated area ID")
    resource_type: str = Field("note", description="Resource type (note, bookmark, file)")
    url: Optional[str] = Field(None, max_length=1000, description="Resource URL")


class ResourceUpdate(BaseModel):
    """Schema for updating a resource"""
    title: Optional[str] = Field(None, max_length=500, description="Resource title")
    content: Optional[str] = Field(None, description="Resource content")
    area_id: Optional[UUID] = Field(None, description="Associated area ID")
    resource_type: Optional[str] = Field(None, description="Resource type")
    url: Optional[str] = Field(None, max_length=1000, description="Resource URL")


class ResourceResponse(BaseModel):
    """Schema for resource response"""
    id: UUID
    user_id: UUID
    area_id: Optional[UUID]
    title: str
    content: Optional[str]
    resource_type: str
    url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Archive Schemas

class ArchiveCreate(BaseModel):
    """Schema for creating an archive entry"""
    parent_type: str = Field(..., description="Type of parent entity (project, area, resource, note)")
    parent_id: UUID = Field(..., description="ID of the parent entity being archived")
    archive_metadata: Optional[str] = Field(None, description="JSON metadata about the archived item")


class ArchiveResponse(BaseModel):
    """Schema for archive response"""
    id: UUID
    user_id: UUID
    parent_type: str
    parent_id: UUID
    archived_at: datetime
    archive_metadata: Optional[str]

    model_config = {"from_attributes": True}
