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

# Schemas will be imported here as they are created
# from .note import NoteCreate, NoteUpdate, NoteResponse
# from .para import AreaCreate, ProjectCreate, ResourceCreate
# from .chat import ChatMessageCreate, ChatMessageResponse
