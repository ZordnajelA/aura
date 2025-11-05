"""
Database models for Aura
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, BigInteger, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, date
from enum import Enum
import uuid

from .database import Base


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class CaptureType(str, Enum):
    """Types of captures"""
    TEXT = "text"
    LINK = "link"
    FILE = "file"


class Capture(Base):
    """Model for captured content"""
    __tablename__ = "captures"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(CaptureType), nullable=False, default=CaptureType.TEXT)
    content = Column(Text, nullable=True)  # For text and links
    file_path = Column(String, nullable=True)  # For uploaded files
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class NoteType(str, Enum):
    """Types of notes"""
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    PDF = "pdf"
    LINK = "link"
    VIDEO = "video"


class Note(Base):
    """Model for notes - core content storage"""
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    note_type = Column(String(50), default="text", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="notes")


class Media(Base):
    """Model for media files attached to notes"""
    __tablename__ = "media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    mime_type = Column(String(100), nullable=True)
    is_processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    note = relationship("Note", backref="media_files")


class DailyNote(Base):
    """Model for daily notes - timeline/log structure"""
    __tablename__ = "daily_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    note_date = Column(Date, nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="daily_notes")


class NoteLink(Base):
    """Model for note-to-note relationships"""
    __tablename__ = "note_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    source_note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String(50), default="related", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    source_note = relationship("Note", foreign_keys=[source_note_id], backref="outgoing_links")
    target_note = relationship("Note", foreign_keys=[target_note_id], backref="incoming_links")


class DailyNoteLink(Base):
    """Model for daily-note-to-note relationships"""
    __tablename__ = "daily_note_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    daily_note_id = Column(UUID(as_uuid=True), ForeignKey("daily_notes.id", ondelete="CASCADE"), nullable=False, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    daily_note = relationship("DailyNote", backref="note_links")
    note = relationship("Note", backref="daily_note_links")


# PARA Note Linking Models

class ResourceNoteLink(Base):
    """Model for resource-to-note relationships"""
    __tablename__ = "resource_note_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    resource = relationship("Resource", backref="note_links")
    note = relationship("Note", backref="resource_links")


class ProjectNoteLink(Base):
    """Model for project-to-note relationships"""
    __tablename__ = "project_note_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", backref="note_links")
    note = relationship("Note", backref="project_links")


class AreaNoteLink(Base):
    """Model for area-to-note relationships"""
    __tablename__ = "area_note_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    area_id = Column(UUID(as_uuid=True), ForeignKey("areas.id", ondelete="CASCADE"), nullable=False, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    area = relationship("Area", backref="note_links")
    note = relationship("Note", backref="area_links")


# PARA Models

class Area(Base):
    """Model for PARA Areas - ongoing responsibilities"""
    __tablename__ = "areas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="areas")


class ProjectStatus(str, Enum):
    """Status values for projects"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    """Model for PARA Projects - goal-oriented initiatives with deadlines"""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    area_id = Column(UUID(as_uuid=True), ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="projects")
    area = relationship("Area", backref="projects")


class ResourceType(str, Enum):
    """Types of resources"""
    NOTE = "note"
    BOOKMARK = "bookmark"
    FILE = "file"


class Resource(Base):
    """Model for PARA Resources - reference materials"""
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    area_id = Column(UUID(as_uuid=True), ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    resource_type = Column(SQLEnum(ResourceType), default=ResourceType.NOTE, nullable=False)
    url = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="resources")
    area = relationship("Area", backref="resources")


class ParentType(str, Enum):
    """Types of parent entities that can be archived"""
    PROJECT = "project"
    AREA = "area"
    RESOURCE = "resource"
    NOTE = "note"


class Archive(Base):
    """Model for PARA Archives - completed or inactive items"""
    __tablename__ = "archives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_type = Column(SQLEnum(ParentType), nullable=False)
    parent_id = Column(UUID(as_uuid=True), nullable=False)
    archived_at = Column(DateTime, default=func.now(), nullable=False)
    archive_metadata = Column("metadata", Text, nullable=True)  # Maps to 'metadata' column in DB

    # Relationships
    user = relationship("User", backref="archives")


# AI Processing Models (Phase 2)

class JobType(str, Enum):
    """Types of AI processing jobs"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    TEXT_CLASSIFICATION = "text_classification"


class JobStatus(str, Enum):
    """Status of processing jobs"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingJob(Base):
    """Model for tracking async AI processing jobs"""
    __tablename__ = "processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    media_id = Column(UUID(as_uuid=True), ForeignKey("media.id", ondelete="CASCADE"), nullable=True, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(SQLEnum(JobType), nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="processing_jobs")
    media = relationship("Media", backref="processing_jobs")
    note = relationship("Note", backref="processing_jobs")


class ContentType(str, Enum):
    """Types of processed content"""
    TRANSCRIPTION = "transcription"
    OCR = "ocr"
    DOCUMENT_TEXT = "document_text"
    SUMMARY = "summary"
    CLASSIFICATION = "classification"


class ProcessedContent(Base):
    """Model for storing AI processing results"""
    __tablename__ = "processed_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    processing_job_id = Column(UUID(as_uuid=True), ForeignKey("processing_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    raw_text = Column(Text, nullable=True)  # Full extracted text
    summary = Column(Text, nullable=True)
    key_points = Column(Text, nullable=True)  # JSON array stored as text
    extracted_tasks = Column(Text, nullable=True)  # JSON array stored as text
    metadata = Column(Text, nullable=True)  # JSON stored as text (provider-specific)
    confidence_score = Column(Integer, nullable=True)  # 0-100
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    note = relationship("Note", backref="processed_content")
    processing_job = relationship("ProcessingJob", backref="processed_content")


class ChatRole(str, Enum):
    """Roles in chat conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(Base):
    """Model for chat interface messages"""
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    role = Column(SQLEnum(ChatRole), nullable=False)
    content = Column(Text, nullable=False)
    context_notes = Column(Text, nullable=True)  # JSON array of note IDs
    suggestions = Column(Text, nullable=True)  # JSON array of suggestion objects
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="chat_messages")


class ClassificationType(str, Enum):
    """Types of content classification"""
    TASK = "task"
    LOG_ENTRY = "log_entry"
    THOUGHT = "thought"
    MEETING_NOTE = "meeting_note"
    INVOICE = "invoice"
    EMAIL = "email"
    REFERENCE = "reference"
    OTHER = "other"


class Priority(str, Enum):
    """Priority levels for classified content"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TextClassification(Base):
    """Model for text classification results"""
    __tablename__ = "text_classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    classification_type = Column(SQLEnum(ClassificationType), nullable=False)
    confidence = Column(Integer, nullable=False)  # 0-100
    suggested_area = Column(String(255), nullable=True)
    suggested_project = Column(String(255), nullable=True)
    is_actionable = Column(Boolean, default=False)
    priority = Column(SQLEnum(Priority), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    note = relationship("Note", backref="classification")
