# app/db/init_db.py

# Caso necessário executar o escript, mas lembre-se de conferir em .env -> INITIALIZE_DB=True
# Em ambiente de produção, na variável de ambiente deixar INITIALIZE_DB=False
# poetry run alembic upgrade head

"""
Database Initialization Module

This module initializes the database with initial data like the superuser
and default roles and permissions.
"""

import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.crud.permission import permission_crud
from app.crud.role import role_crud
from app.crud.user import user_crud
from app.db.session import AsyncSessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.schemas.permission import PermissionCreate
from app.schemas.role import RoleCreate
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


async def init_permissions(db: AsyncSession) -> List[Permission]:
    default_permissions = [
        {"name": "User Read", "code": "user:read", "description": "Can view users"},
        {"name": "User Create", "code": "user:create", "description": "Can create users"},
        {"name": "User Update", "code": "user:update", "description": "Can update users"},
        {"name": "User Delete", "code": "user:delete", "description": "Can delete users"},
        {"name": "Role Read", "code": "role:read", "description": "Can view roles"},
        {"name": "Role Create", "code": "role:create", "description": "Can create roles"},
        {"name": "Role Update", "code": "role:update", "description": "Can update roles"},
        {"name": "Role Delete", "code": "role:delete", "description": "Can delete roles"},
    ]

    permissions = []
    for perm_data in default_permissions:
        permission = await permission_crud.get_by_code(db, code=perm_data["code"])
        if permission:
            logger.info(f"🟡 Permissão já existe: {permission.code}")
            permissions.append(permission)
            continue
        perm_in = PermissionCreate(**perm_data)
        permission = await permission_crud.create(db, obj_in=perm_in)
        logger.info(f"🟢 Permissão criada: {permission.code}")
        permissions.append(permission)

    await db.commit()
    return permissions


async def init_roles(db: AsyncSession, permissions: List[Permission]) -> List[Role]:
    all_perm_ids = [str(p.id) for p in permissions]
    user_perm_ids = [str(p.id) for p in permissions if p.code.startswith("user:read")]

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
    ]

    roles = []
    for role_data in default_roles:
        role = await role_crud.get_by_code(db, code=role_data["code"])
        if not role:
            role_in = RoleCreate(
                name=role_data["name"],
                code=role_data["code"],
                description=role_data["description"],
            )
            role = await role_crud.create_with_permissions(
                db, obj_in=role_in, permission_ids=role_data["permission_ids"]
            )
            logger.info(f"🟢 Role criada: {role.code}")
        else:
            logger.info(f"🟡 Role já existe: {role.code}")
        roles.append(role)

    await db.commit()
    return roles


# Create superuser
async def init_superuser(db: AsyncSession, roles: List[Role]) -> None:
    if settings.FIRST_SUPERUSER_EMAIL and settings.FIRST_SUPERUSER_PASSWORD:
        result = await db.execute(
            User.__table__.select().where(User.email == settings.FIRST_SUPERUSER_EMAIL)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.info(f"🟡 Superusuário já existe: {settings.FIRST_SUPERUSER_EMAIL}")
            return

        admin_role_id = next((str(r.id) for r in roles if r.code == "admin"), None)
        role_ids = [admin_role_id] if admin_role_id else []

        new_user = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True,
        )

        db.add(new_user)
        await db.commit()
        logger.info(f"🟢 Superusuário criado: {new_user.email}")


async def init_db() -> None:
    logger.info("🧩 Inicializando o banco de dados...")
    async with AsyncSessionLocal() as db:
        permissions = await init_permissions(db)
        roles = await init_roles(db, permissions)
        await init_superuser(db, roles)
    logger.info("✅ Inicialização do banco de dados concluída.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())
