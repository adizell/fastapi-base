"""
Authentication Service Module

This module handles authentication and token management services.
"""
from typing import List, Optional

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    validate_access_token,
    validate_refresh_token,
)
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.token import Token


class AuthService:
    """
    Authentication service for handling user authentication and tokens.
    """

    @staticmethod
    async def authenticate(
        db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            db: Database session
            email: User email
            password: User password

        Returns:
            Optional[User]: Authenticated user or None
        """
        return await user_crud.authenticate(db, email=email, password=password)

    @staticmethod
    async def create_tokens(user: User) -> Token:
        """
        Create access and refresh tokens for a user.

        Args:
            user: User object

        Returns:
            Token: Token response with access and refresh tokens
        """
        # Extract user roles and permissions for token scopes
        scopes = []

        # Add role codes
        for role in user.roles:
            scopes.append(f"role:{role.code}")

            # Add permission codes
            for permission in role.permissions:
                scopes.append(permission.code)

        # Remove duplicates while preserving order
        unique_scopes = []
        for scope in scopes:
            if scope not in unique_scopes:
                unique_scopes.append(scope)

        # Create tokens
        access_token = create_access_token(subject=user.id, scopes=unique_scopes)
        refresh_token = create_refresh_token(subject=user.id)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @staticmethod
    async def refresh_token(db: AsyncSession, refresh_token: str) -> Token:
        """
        Refresh access token using a valid refresh token.

        Args:
            db: Database session
            refresh_token: JWT refresh token

        Returns:
            Token: New token pair

        Raises:
            UnauthorizedError: If refresh token is invalid
        """
        try:
            # Validate refresh token
            payload = validate_refresh_token(refresh_token)
            user_id = payload.get("sub")

            if not user_id:
                raise UnauthorizedError("Invalid refresh token")

            # Get user
            user = await user_crud.get_user_with_roles(db, user_id=user_id)
            if not user:
                raise UnauthorizedError("User not found")

            if not user.is_active:
                raise UnauthorizedError("Inactive user")

            # Create new tokens
            return await AuthService.create_tokens(user)

        except JWTError:
            raise UnauthorizedError("Invalid refresh token")

    @staticmethod
    async def validate_token_scopes(token: str, required_scopes: List[str]) -> bool:
        """
        Validate if token has required scopes.

        Args:
            token: JWT token
            required_scopes: List of required scopes

        Returns:
            bool: True if token has all required scopes

        Raises:
            UnauthorizedError: If token is invalid
            ForbiddenError: If token lacks required scopes
        """
        try:
            payload = validate_access_token(token)
            token_scopes = payload.get("scopes", [])

            # Check if token has all required scopes
            for scope in required_scopes:
                if scope not in token_scopes:
                    raise ForbiddenError(f"Missing required scope: {scope}")

            return True

        except JWTError:
            raise UnauthorizedError("Invalid token")


# Create singleton instance
auth_service = AuthService()
