"""
Database models for Aura
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Enum as SQLEnum, ForeignKey
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
