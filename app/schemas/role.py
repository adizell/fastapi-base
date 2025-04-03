"""
Role Schema Module

This module defines Pydantic schemas for role data validation and serialization.
"""
from typing import List, Optional

from pydantic import Field

from app.schemas.base import BaseProperties, BaseSchema


class RoleBase(BaseSchema):
    """
    Base role schema with common role attributes.

    Attributes:
        name: Human-readable role name
        code: Unique role code
        description: Optional role description
    """

    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z0-9_]+$")
    description: Optional[str] = Field(None, max_length=255)


class RoleCreate(RoleBase):
    """Schema for role creation."""
    pass


class RoleUpdate(BaseSchema):
    """
    Schema for role updates.

    All fields are optional to allow partial updates.

    Attributes:
        name: Human-readable role name
        description: Role description
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class RoleResponse(RoleBase, BaseProperties):
    """
    Schema for role responses.

    Inherits from RoleBase and BaseProperties.
    """
    pass


class RoleDetailResponse(RoleResponse):
    """
    Schema for detailed role responses, including permissions.

    Attributes:
        permissions: List of role permissions
    """

    from app.schemas.permission import PermissionResponse
    permissions: List[PermissionResponse] = []


class RoleWithPermissions(BaseSchema):
    """
    Schema for adding/updating role permissions.

    Attributes:
        permission_ids: List of permission IDs to assign to role
    """

    permission_ids: List[str]
