"""
Database Initialization Module

This module initializes the database with initial data like the superuser
and default roles and permissions.
"""
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.permission import permission_crud
from app.crud.role import role_crud
from app.crud.user import user_crud
from app.db.session import AsyncSessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.schemas.permission import PermissionCreate
from app.schemas.role import RoleCreate
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


async def init_permissions(db: AsyncSession) -> List[Permission]:
    """
    Initialize system permissions.

    Args:
        db: Database session

    Returns:
        List[Permission]: Created permissions
    """
    # Define default permissions
    default_permissions = [
        {"name": "User Read", "code": "user:read", "description": "Can view users"},
        {
            "name": "User Create",
            "code": "user:create",
            "description": "Can create users",
        },
        {
            "name": "User Update",
            "code": "user:update",
            "description": "Can update users",
        },
        {
            "name": "User Delete",
            "code": "user:delete",
            "description": "Can delete users",
        },
        {"name": "Role Read", "code": "role:read", "description": "Can view roles"},
        {
            "name": "Role Create",
            "code": "role:create",
            "description": "Can create roles",
        },
        {
            "name": "Role Update",
            "code": "role:update",
            "description": "Can update roles",
        },
        {
            "name": "Role Delete",
            "code": "role:delete",
            "description": "Can delete roles",
        },
        # Add more permissions as needed
    ]

    permissions = []
    for perm_data in default_permissions:
        # Check if permission already exists
        permission = await permission_crud.get_by_code(db, code=perm_data["code"])
        if not permission:
            # Create permission if it doesn't exist
            perm_in = PermissionCreate(**perm_data)
            permission = await permission_crud.create(db, obj_in=perm_in)
            logger.info(f"Created permission: {permission.code}")
        permissions.append(permission)

    return permissions


async def init_roles(db: AsyncSession, permissions: List[Permission]) -> List[Role]:
    """
    Initialize system roles.

    Args:
        db: Database session
        permissions: List of system permissions

    Returns:
        List[Role]: Created roles
    """
    # Get all permission IDs
    all_perm_ids = [str(p.id) for p in permissions]
    user_perm_ids = [str(p.id) for p in permissions if p.code.startswith("user:read")]

    # Define default roles
    default_roles = [
        {
            "name": "Admin",
            "code": "admin",
            "description": "Administrator role with all permissions",
            "permission_ids": all_perm_ids,
        },
        {
            "name": "User",
            "code": "user",
            "description": "Regular user with limited permissions",
            "permission_ids": user_perm_ids,
        },
        # Add more roles as needed
    ]

    roles = []
    for role_data in default_roles:
        # Check if role already exists
        role = await role_crud.get_by_code(db, code=role_data["code"])
        if not role:
            # Create role if it doesn't exist
            role_in = RoleCreate(
                name=role_data["name"],
                code=role_data["code"],
                description=role_data["description"],
            )
            role = await role_crud.create_with_permissions(
                db, obj_in=role_in, permission_ids=role_data["permission_ids"]
            )
            logger.info(f"Created role: {role.code}")
        roles.append(role)

    return roles


async def init_superuser(db: AsyncSession, roles: List[Role]) -> None:
    """
    Initialize the superuser account if configured.

    Args:
        db: Database session
        roles: List of system roles

    Returns:
        None
    """
    # Check if superuser creation is configured
    if settings.FIRST_SUPERUSER_EMAIL and settings.FIRST_SUPERUSER_PASSWORD:
        # Check if superuser already exists
        user = await user_crud.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not user:
            # Get admin role ID
            admin_role_id = next((str(r.id) for r in roles if r.code == "admin"), None)
            role_ids = [admin_role_id] if admin_role_id else []

            # Create superuser
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                is_active=True,
                full_name="System Administrator",
            )
            user = await user_crud.create_with_roles(
                db, obj_in=user_in, role_ids=role_ids
            )
            logger.info(f"Created superuser: {user.email}")


async def init_db() -> None:
    """
    Initialize database with initial data.

    Creates default permissions, roles, and superuser if configured.

    Returns:
        None
    """
    logger.info("Initializing database")

    async with AsyncSessionLocal() as db:
        # Create permissions
        permissions = await init_permissions(db)

        # Create roles
        roles = await init_roles(db, permissions)

        # Create superuser
        await init_superuser(db, roles)

    logger.info("Database initialization completed")
