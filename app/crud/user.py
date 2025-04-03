"""
User CRUD Module

This module defines CRUD operations specific to the User model.
"""
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model.

    Extends the base CRUD class with user-specific operations.
    """

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            Optional[User]: Found user or None
        """
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        Create a new user with hashed password.

        Args:
            db: Database session
            obj_in: User create schema

        Returns:
            User: Created user
        """
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def create_with_roles(
            self,
            db: AsyncSession,
            *,
            obj_in: UserCreate,
            role_ids: List[str]
    ) -> User:
        """
        Create a new user with assigned roles.

        Args:
            db: Database session
            obj_in: User create schema
            role_ids: List of role IDs to assign

        Returns:
            User: Created user with roles
        """
        # Create user
        user = await self.create(db, obj_in=obj_in)

        # Assign roles if provided
        if role_ids:
            query = select(Role).where(Role.id.in_(role_ids))
            result = await db.execute(query)
            roles = result.scalars().all()
            user.roles = roles
            db.add(user)
            await db.flush()
            await db.refresh(user)

        return user

    async def update(
            self,
            db: AsyncSession,
            *,
            db_obj: User,
            obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user, handling password hashing if needed.

        Args:
            db: Database session
            db_obj: Existing user object
            obj_in: User update schema or dict

        Returns:
            User: Updated user
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Hash password if provided
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
            self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            db: Database session
            email: User email
            password: Plain password

        Returns:
            Optional[User]: Authenticated user or None
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def is_active(self, user: User) -> bool:
        """
        Check if user is active.

        Args:
            user: User object

        Returns:
            bool: True if user is active
        """
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """
        Check if user is superuser.

        Args:
            user: User object

        Returns:
            bool: True if user is superuser
        """
        return user.is_superuser

    async def get_user_with_roles(self, db: AsyncSession, *, user_id: str) -> Optional[User]:
        """
        Get user with eagerly loaded roles.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Optional[User]: User with roles or None
        """
        query = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def update_user_roles(
            self,
            db: AsyncSession,
            *,
            user_id: str,
            role_ids: List[str]
    ) -> Optional[User]:
        """
        Update user's roles.

        Args:
            db: Database session
            user_id: User ID
            role_ids: List of role IDs to assign

        Returns:
            Optional[User]: Updated user with roles or None
        """
        user = await self.get_user_with_roles(db, user_id=user_id)
        if not user:
            return None

        # Get roles by IDs
        query = select(Role).where(Role.id.in_(role_ids))
        result = await db.execute(query)
        roles = result.scalars().all()

        # Update user's roles
        user.roles = roles
        db.add(user)
        await db.flush()
        await db.refresh(user)

        return user


# Create singleton instance
user_crud = CRUDUser(User)
