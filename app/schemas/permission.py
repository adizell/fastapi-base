"""
Permission Schema Module

This module defines Pydantic schemas for permission data validation and serialization.
"""
from typing import Optional

from pydantic import Field

from app.schemas.base import BaseProperties, BaseSchema


class PermissionBase(BaseSchema):
    """
    Base permission schema with common permission attributes.

    Attributes:
        name: Human-readable permission name
        code: Unique permission code (e.g., 'user:read')
        description: Optional permission description
    """

    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9_:]+$")
    description: Optional[str] = Field(None, max_length=255)


class PermissionCreate(PermissionBase):
    """Schema for permission creation."""


class PermissionUpdate(BaseSchema):
    """
    Schema for permission updates.

    All fields are optional to allow partial updates.

    Attributes:
        name: Human-readable permission name
        description: Permission description
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class PermissionResponse(PermissionBase, BaseProperties):
    """
    Schema for permission responses.

    Inherits from PermissionBase and BaseProperties.
    """
