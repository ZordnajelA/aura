"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import get_db
from ..models import User
from ..schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse
)
from ..utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token
)
from .dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user

    Args:
        user_data: User registration data (email and password)
        db: Database session

    Returns:
        UserResponse with user information (excluding password)

    Raises:
        HTTPException: If email already exists
    """
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    password_hash = get_password_hash(user_data.password)

    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=password_hash
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login and receive access token

    Args:
        credentials: User login credentials (email and password)
        db: Database session

    Returns:
        TokenResponse with access_token and refresh_token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access and refresh tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information

    Args:
        current_user: Current authenticated user from JWT token

    Returns:
        UserResponse with current user information
    """
    return current_user
