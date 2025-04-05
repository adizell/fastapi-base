# app/models/role.py
"""
Role Model Module

This module defines the Role model and related SQLAlchemy models.
"""
from typing import List, Optional

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Association table for many-to-many relationship between roles and permissions
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column(
        "role_id",
        String(36),
        ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        String(36),
        ForeignKey("permission.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(Base):
    """
    Role model representing user roles with associated permissions.

    Attributes:
        name: Human-readable role name
        code: Unique role code used for identification
        description: Optional description of the role
        permissions: Many-to-many relationship with permissions
        users: Many-to-many relationship with users
    """

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permission,
        back_populates="roles",
        lazy="selectin",
    )

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="user_role",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation of Role instance."""
        return f"<Role {self.code}>"
