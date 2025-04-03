"""
User Model Module

This module defines the User model and related SQLAlchemy models.
"""
from sqlalchemy import Boolean, Column, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

# Association table for many-to-many relationship between users and roles
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", String(36), ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """
    User model representing application users.

    Attributes:
        email: Unique email address
        hashed_password: Hashed user password
        full_name: User's full name
        is_active: Whether user account is active
        is_superuser: Whether user has superuser privileges
        roles: Many-to-many relationship with roles
    """

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Many-to-many relationship with Role model
    roles = relationship(
        "Role",
        secondary=user_role,
        back_populates="users",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation of User instance."""
        return f"<User {self.email}>"
