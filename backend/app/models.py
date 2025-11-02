"""
Database models for Aura
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
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
