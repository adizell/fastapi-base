"""
Role Schema Module

This module defines Pydantic schemas for role data validation and serialization.
"""
from typing import List, Optional

from pydantic import Field

from app.schemas.base import BaseProperties, BaseSchema
from app.schemas.permission import PermissionResponse


class RoleBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z0-9_]+$")
    description: Optional[str] = Field(None, max_length=255)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class RoleResponse(RoleBase, BaseProperties):
    pass


class RoleDetailResponse(RoleResponse):
    permissions: List[PermissionResponse] = []


class RoleWithPermissions(BaseSchema):
    permission_ids: List[str]
