"""
Permission CRUD Module

This module defines CRUD operations specific to the Permission model.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    """
    CRUD operations for Permission model.

    Extends the base CRUD class with permission-specific operations.
    """

    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Permission]:
        """
        Get a permission by code.

        Args:
            db: Database session
            code: Permission code

        Returns:
            Optional[Permission]: Found permission or None
        """
        query = select(Permission).where(Permission.code == code)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_with_roles(self, db: AsyncSession, *, permission_id: str) -> Optional[Permission]:
        """
        Get permission with eagerly loaded roles.

        Args:
            db: Database session
            permission_id: Permission ID

        Returns:
            Optional[Permission]: Permission with roles or None
        """
        query = (
            select(Permission)
            .options(selectinload(Permission.roles))
            .where(Permission.id == permission_id)
        )
        result = await db.execute(query)
        return result.scalars().first()


# Create singleton instance
permission_crud = CRUDPermission(Permission)
