"""
Role CRUD Module

This module defines CRUD operations specific to the Role model.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.permission import Permission
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    """
    CRUD operations for Role model.

    Extends the base CRUD class with role-specific operations.
    """

    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Role]:
        """
        Get a role by code.

        Args:
            db: Database session
            code: Role code

        Returns:
            Optional[Role]: Found role or None
        """
        query = select(Role).where(Role.code == code)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_with_permissions(self, db: AsyncSession, *, role_id: str) -> Optional[Role]:
        """
        Get role with eagerly loaded permissions.

        Args:
            db: Database session
            role_id: Role ID

        Returns:
            Optional[Role]: Role with permissions or None
        """
        query = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def create_with_permissions(
            self,
            db: AsyncSession,
            *,
            obj_in: RoleCreate,
            permission_ids: List[str]
    ) -> Role:
        """
        Create a new role with assigned permissions.

        Args:
            db: Database session
            obj_in: Role create schema
            permission_ids: List of permission IDs to assign

        Returns:
            Role: Created role with permissions
        """
        # Create role
        role = await self.create(db, obj_in=obj_in)

        # Assign permissions if provided
        if permission_ids:
            query = select(Permission).where(Permission.id.in_(permission_ids))
            result = await db.execute(query)
            permissions = result.scalars().all()
            role.permissions = permissions
            db.add(role)
            await db.flush()
            await db.refresh(role)

        return role

    async def update_role_permissions(
            self,
            db: AsyncSession,
            *,
            role_id: str,
            permission_ids: List[str]
    ) -> Optional[Role]:
        """
        Update role's permissions.

        Args:
            db: Database session
            role_id: Role ID
            permission_ids: List of permission IDs to assign

        Returns:
            Optional[Role]: Updated role with permissions or None
        """
        role = await self.get_with_permissions(db, role_id=role_id)
        if not role:
            return None

        # Get permissions by IDs
        query = select(Permission).where(Permission.id.in_(permission_ids))
        result = await db.execute(query)
        permissions = result.scalars().all()

        # Update role's permissions
        role.permissions = permissions
        db.add(role)
        await db.flush()
        await db.refresh(role)

        return role

    async def get_role_with_users(self, db: AsyncSession, *, role_id: str) -> Optional[Role]:
        """
        Get role with eagerly loaded users.

        Args:
            db: Database session
            role_id: Role ID

        Returns:
            Optional[Role]: Role with users or None
        """
        query = (
            select(Role)
            .options(selectinload(Role.users))
            .where(Role.id == role_id)
        )
        result = await db.execute(query)
        return result.scalars().first()


# Create singleton instance
role_crud = CRUDRole(Role)
