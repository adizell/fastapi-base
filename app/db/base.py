# app/db/base.py
"""
SQLAlchemy Base Model Module

This module defines the base model for all SQLAlchemy models in the application.
"""
import uuid
from datetime import datetime
from typing import ClassVar

from sqlalchemy import DateTime, String
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import now


@as_declarative()
class Base:
    """
    Base class for all SQLAlchemy models.

    Provides:
        - Automatic table name generation
        - Default id column as UUID
        - Created and updated timestamp columns
    """

    __name__: ClassVar[str]

    # Primary key as UUID
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=now(), onupdate=now(), nullable=False
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Generate table name automatically based on class name.

        Returns:
            str: Table name (usually in snake_case)
        """
        # Convert CamelCase to snake_case
        name = cls.__name__
        return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip(
            "_"
        )

    def dict(self) -> dict:
        """
        Convert model instance to dictionary.

        Returns:
            dict: Model data as dictionary
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
