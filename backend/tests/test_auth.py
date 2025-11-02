"""
Tests for authentication endpoints and utilities
"""

import pytest
from uuid import uuid4
from datetime import timedelta

from app.utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "test_password_123"
    hashed = get_password_hash(password)

    # Verify correct password
    assert verify_password(password, hashed) is True

    # Verify incorrect password
    assert verify_password("wrong_password", hashed) is False


def test_access_token_creation_and_decoding():
    """Test JWT access token creation and decoding"""
    user_id = uuid4()
    user_email = "test@example.com"

    # Create token
    token = create_access_token(
        data={"sub": str(user_id), "email": user_email}
    )

    # Verify token is a string
    assert isinstance(token, str)
    assert len(token) > 0

    # Decode token
    token_data = decode_token(token)

    # Verify decoded data
    assert token_data.user_id == user_id
    assert token_data.email == user_email


def test_refresh_token_creation():
    """Test JWT refresh token creation"""
    user_id = uuid4()
    user_email = "test@example.com"

    # Create refresh token
    token = create_refresh_token(
        data={"sub": str(user_id), "email": user_email}
    )

    # Verify token is a string
    assert isinstance(token, str)
    assert len(token) > 0

    # Decode token
    token_data = decode_token(token)

    # Verify decoded data
    assert token_data.user_id == user_id
    assert token_data.email == user_email


def test_token_expiration():
    """Test token expiration"""
    user_id = uuid4()

    # Create token with very short expiration (negative means already expired)
    token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(seconds=-1)
    )

    # Attempting to decode expired token should raise JWTError
    from jose import JWTError
    with pytest.raises(JWTError):
        decode_token(token)


def test_password_hash_uniqueness():
    """Test that same password produces different hashes (due to salt)"""
    password = "test_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    # Hashes should be different due to random salt
    assert hash1 != hash2

    # But both should verify correctly
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)
