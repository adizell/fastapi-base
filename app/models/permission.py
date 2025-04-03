"""
Permission Model Module

This module defines the Permission model for granular access control.
"""
from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Permission(Base):
    """
    Permission model representing granular access controls.

    Attributes:
        name: Human-readable permission name
        code: Unique permission code (e.g., 'user:read')
        description: Optional description of the permission
        roles: Many-to-many relationship with roles
    """

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="role_permission",
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation of Permission instance."""
        return f"<Permission {self.code}>"
