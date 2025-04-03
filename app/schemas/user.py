"""
User Schema Module

This module defines Pydantic schemas for user data validation and serialization.
"""
from typing import List, Optional

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import BaseProperties, BaseSchema
from app.schemas.role import RoleResponse


class UserBase(BaseSchema):
    """
    Base user schema with common user attributes.

    Attributes:
        email: User email
        full_name: User full name
        is_active: Whether user is active
        is_superuser: Whether user is a superuser
    """

    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """
    Schema for user creation.

    Attributes:
        password: User password (8-64 characters)
        password_confirm: Password confirmation (must match password)
    """

    password: str = Field(..., min_length=8, max_length=64)
    password_confirm: Optional[str] = Field(None, min_length=8, max_length=64)

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v: Optional[str], info) -> Optional[str]:
        """Validate that passwords match."""
        if "password" in info.data and v is not None and info.data["password"] != v:
            raise ValueError("Passwords do not match")
        return v


class UserUpdate(BaseSchema):
    """
    Schema for user updates.

    All fields are optional to allow partial updates.

    Attributes:
        email: User email
        full_name: User full name
        password: User password
        is_active: Whether user is active
        is_superuser: Whether user is a superuser
    """

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=64)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(UserBase, BaseProperties):
    """
    Schema for user responses.

    Inherits from UserBase and BaseProperties.
    """

    pass


class UserDetailResponse(UserResponse):
    """
    Schema for detailed user responses, including roles.

    Attributes:
        roles: List of user roles
    """

    roles: List[RoleResponse] = []


class UserWithRoles(BaseSchema):
    """
    Schema for adding/updating user roles.

    Attributes:
        role_ids: List of role IDs to assign to user
    """

    role_ids: List[str]
