# app/db/init_superuser.py
"""
Superuser Initialization Script

This script ensures a superuser is created in the database
based on environment configuration, using SQLAlchemy async.
"""

# No terminal, vá até a pasta raiz do projeto (fastapi-base) e execute:
# cd C:\pycharm\fastapi-base
# poetry run python app/db/init_superuser.py

import os
import sys

from dotenv import load_dotenv

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Carrega o .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

import asyncio

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.user import User


async def create_superuser():
    async with AsyncSessionLocal() as session:
        # Verifica se o superusuário já existe
        result = await session.execute(
            User.__table__.select().where(User.email == settings.FIRST_SUPERUSER_EMAIL)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"🟡 Superusuário '{settings.FIRST_SUPERUSER_EMAIL}' já existe.")
            return

        # Cria novo superusuário
        new_user = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True,
        )

        session.add(new_user)
        await session.commit()
        print(f"🟢 Superusuário '{new_user.email}' criado com sucesso!")


if __name__ == "__main__":
    try:
        asyncio.run(create_superuser())
    except Exception as e:
        print(f"🔴 Erro ao criar superusuário: {e}")
