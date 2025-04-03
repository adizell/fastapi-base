"""
SQLAlchemy Base Model Module

This module defines the base model for all SQLAlchemy models in the application.
"""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Base class for all SQLAlchemy models.

    Provides:
        - Automatic table name generation
        - Default id column as UUID
        - Created and updated timestamp columns
    """

    id: Any
    __name__: str

    # Primary key as UUID
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate table name automatically based on class name.

        Returns:
            str: Table name (usually in snake_case)
        """
        # Convert CamelCase to snake_case
        name = cls.__name__
        return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')

    def dict(self) -> dict:
        """
        Convert model instance to dictionary.

        Returns:
            dict: Model data as dictionary
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
