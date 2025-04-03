"""
Permission Model Module

This module defines the Permission model for granular access control.
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

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

    name = Column(String(100), nullable=False)
    code = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    # Relationships
    roles = relationship(
        "Role",
        secondary="role_permission",
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation of Permission instance."""
        return f"<Permission {self.code}>"
