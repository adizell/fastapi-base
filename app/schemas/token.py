"""
Token Schema Module

This module defines Pydantic schemas for token validation and serialization.
"""
from typing import List, Optional

from app.schemas.base import BaseSchema


class Token(BaseSchema):
    """
    Schema for token response.

    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token for obtaining new access tokens
        token_type: Token type (always 'bearer')
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseSchema):
    """
    Schema for token payload.

    Attributes:
        sub: Subject (user ID)
        exp: Expiration timestamp
        type: Token type ('access' or 'refresh')
        scopes: Optional permission scopes
    """

    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None
    scopes: Optional[List[str]] = None


class TokenData(BaseSchema):
    """
    Schema for validated token data.

    Attributes:
        user_id: User ID from token
        scopes: User permission scopes
    """

    user_id: str
    scopes: List[str] = []


class RefreshToken(BaseSchema):
    """
    Schema for token refresh requests.

    Attributes:
        refresh_token: JWT refresh token
    """

    refresh_token: str


class TokenRevoke(BaseSchema):
    """
    Schema for token revocation requests.

    Attributes:
        token: JWT token to revoke
    """

    token: str
