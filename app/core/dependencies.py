"""
Dependency Injection Module

This module defines FastAPI dependencies for authentication, authorization,
and other common requirements across the application.
"""
from typing import Any, List, Optional, Set, Union

from fastapi import Depends, Header, Query, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import validate_access_token
from app.crud.user import user_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenData

# OAuth2 scheme for token handling
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/v1/auth/login"
)


async def get_token_data(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Validate access token and extract token data.

    Args:
        token: JWT token from request

    Returns:
        TokenData: Validated token data

    Raises:
        UnauthorizedError: If token is invalid
    """
    try:
        payload = validate_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError("Could not validate credentials")

        token_scopes = payload.get("scopes", [])
        return TokenData(user_id=user_id, scopes=token_scopes)

    except JWTError:
        raise UnauthorizedError("Could not validate credentials")


async def get_current_user(
        db: AsyncSession = Depends(get_db),
        token_data: TokenData = Depends(get_token_data),
) -> User:
    """
    Get the current authenticated user.

    Args:
        db: Database session
        token_data: Validated token data

    Returns:
        User: Current authenticated user

    Raises:
        UnauthorizedError: If user not found or inactive
    """
    user = await user_crud.get(db, id=token_data.user_id)
    if not user:
        raise UnauthorizedError("User not found")

    if not user.is_active:
        raise UnauthorizedError("Inactive user")

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the current user is active.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current active user

    Raises:
        UnauthorizedError: If user is inactive
    """
    if not current_user.is_active:
        raise UnauthorizedError("Inactive user")

    return current_user


async def get_current_superuser(
        current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Ensure the current user is a superuser.

    Args:
        current_user: Current authenticated active user

    Returns:
        User: Current superuser

    Raises:
        ForbiddenError: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise ForbiddenError("Superuser privileges required")

    return current_user


def require_permissions(required_permissions: List[str]):
    """
    Create a dependency that checks for specific permissions.

    Args:
        required_permissions: List of permissions the user must have

    Returns:
        Dependency function that validates user permissions
    """

    async def _check_permissions(
            current_user: User = Depends(get_current_active_user),
    ) -> User:
        """
        Check if the current user has all required permissions.

        Args:
            current_user: Current authenticated active user

        Returns:
            User: Current user with verified permissions

        Raises:
            ForbiddenError: If user lacks required permissions
        """
        if current_user.is_superuser:
            return current_user

        # Get all permission codes from user roles
        user_permissions: Set[str] = set()
        for role in current_user.roles:
            for permission in role.permissions:
                user_permissions.add(permission.code)

        # Check if user has all required permissions
        missing_permissions = [
            p for p in required_permissions if p not in user_permissions
        ]

        if missing_permissions:
            raise ForbiddenError(f"Missing required permissions: {', '.join(missing_permissions)}")

        return current_user

    return _check_permissions


def require_any_permission(required_permissions: List[str]):
    """
    Create a dependency that checks if user has any of the specified permissions.

    Args:
        required_permissions: List of permissions (having any one is sufficient)

    Returns:
        Dependency function that validates user permissions
    """

    async def _check_any_permission(
            current_user: User = Depends(get_current_active_user),
    ) -> User:
        """
        Check if the current user has any of the required permissions.

        Args:
            current_user: Current authenticated active user

        Returns:
            User: Current user with verified permissions

        Raises:
            ForbiddenError: If user lacks all required permissions
        """
        if current_user.is_superuser:
            return current_user

        # Get all permission codes from user roles
        user_permissions: Set[str] = set()
        for role in current_user.roles:
            for permission in role.permissions:
                user_permissions.add(permission.code)

        # Check if user has any of the required permissions
        has_any = any(p in user_permissions for p in required_permissions)

        if not has_any:
            raise ForbiddenError(f"Required at least one of these permissions: {', '.join(required_permissions)}")

        return current_user

    return _check_any_permission


def require_role(role_code: str):
    """
    Create a dependency that checks if user has a specific role.

    Args:
        role_code: Role code the user must have

    Returns:
        Dependency function that validates user role
    """

    async def _check_role(
            current_user: User = Depends(get_current_active_user),
    ) -> User:
        """
        Check if the current user has the specified role.

        Args:
            current_user: Current authenticated active user

        Returns:
            User: Current user with verified role

        Raises:
            ForbiddenError: If user doesn't have the role
        """
        if current_user.is_superuser:
            return current_user

        # Check if user has the role
        has_role = any(role.code == role_code for role in current_user.roles)

        if not has_role:
            raise ForbiddenError(f"Required role: {role_code}")

        return current_user

    return _check_role


async def parse_pagination_params(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict:
    """
    Parse and validate pagination parameters.

    Args:
        page: Page number (1-based)
        page_size: Number of items per page

    Returns:
        dict: Pagination parameters
    """
    return {
        "skip": (page - 1) * page_size,
        "limit": page_size,
        "page": page,
        "page_size": page_size,
    }


async def check_rate_limit(
        request: Request,
        user: Optional[User] = None,
        limit: Optional[int] = None,
) -> None:
    """
    Check if request rate limit is exceeded.

    This is a placeholder for a rate limiting implementation.
    You would typically use Redis to track request counts.

    Args:
        request: The incoming request
        user: Optional authenticated user
        limit: Optional custom limit for this endpoint

    Raises:
        RateLimitError: If rate limit is exceeded
    """
    # Implement rate limiting logic here
    # Example with Redis would track requests per minute by IP or user ID
    pass
