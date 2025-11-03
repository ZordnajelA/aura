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
from .para import (
    AreaCreate,
    AreaUpdate,
    AreaResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    ArchiveCreate,
    ArchiveResponse
)

# Schemas will be imported here as they are created
# from .chat import ChatMessageCreate, ChatMessageResponse
