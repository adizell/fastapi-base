"""
Security Module

This module handles password hashing, JWT token creation and verification,
and other security-related functionality.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: Union[str, Any], scopes: list = None,
                        expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        subject: The subject of the token (typically user ID)
        scopes: Permission scopes to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.utcnow(),
    }

    if scopes:
        to_encode["scopes"] = scopes

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        subject: The subject of the token (typically user ID)

    Returns:
        str: Encoded JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.utcnow(),
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain-text password
        hashed_password: Hashed password

    Returns:
        bool: True if password matches hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a password hash.

    Args:
        password: Plain-text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Dict containing the token payload

    Raises:
        jwt.JWTError: If token is invalid or expired
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )


def validate_access_token(token: str) -> Dict[str, Any]:
    """
    Validate an access token and ensure it's not a refresh token.

    Args:
        token: JWT token to validate

    Returns:
        Dict containing the token payload

    Raises:
        jwt.JWTError: If token is invalid, expired, or wrong type
    """
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise jwt.JWTError("Not an access token")
    return payload


def validate_refresh_token(token: str) -> Dict[str, Any]:
    """
    Validate a refresh token and ensure it's not an access token.

    Args:
        token: JWT token to validate

    Returns:
        Dict containing the token payload

    Raises:
        jwt.JWTError: If token is invalid, expired, or wrong type
    """
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise jwt.JWTError("Not a refresh token")
    return payload
