"""
API dependencies for authentication and authorization
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from ..database import get_db
from ..models import User
from ..utils.auth import decode_token

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token

    Args:
        credentials: HTTP Authorization credentials with Bearer token
        db: Database session

    Returns:
        User object of the authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from credentials
        token = credentials.credentials

        # Decode the JWT token
        token_data = decode_token(token)

        if token_data.user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current active user

    This can be extended in the future to check if user is active/enabled

    Args:
        current_user: Current authenticated user

    Returns:
        User object if active

    Raises:
        HTTPException: If user is inactive
    """
    # Future: Add check for user.is_active field if needed
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
