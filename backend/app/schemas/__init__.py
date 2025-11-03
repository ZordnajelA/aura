"""
Pydantic schemas for request/response validation
"""

from .capture import CaptureCreate, CaptureResponse, CaptureType
from .auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    TokenData
)
from .note import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    NoteLinkCreate,
    NoteLinkResponse
)
from .daily_notes import (
    DailyNoteCreate,
    DailyNoteUpdate,
    DailyNoteResponse,
    DailyNoteLinkCreate,
    DailyNoteLinkResponse
)

# Schemas will be imported here as they are created
# from .para import AreaCreate, ProjectCreate, ResourceCreate
# from .chat import ChatMessageCreate, ChatMessageResponse
