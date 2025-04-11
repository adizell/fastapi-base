"""
User Endpoints Module

This module defines routes for user management.
"""
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import parse_pagination_params
from app.core.dependencies import (
    get_current_active_user,
    get_current_superuser,
    require_permissions,
)
from app.crud.user import user_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.user import (
    UserCreate,
    UserDetailResponse,
    UserResponse,
    UserUpdate,
    UserWithRoles,
)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    pagination: dict = Depends(parse_pagination_params),
    search: Optional[str] = Query(None, description="Search by email or full name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    _: User = Depends(require_permissions(["user:read"])),
) -> Any:
    """
    Get all users with pagination.

    Args:
        db: Database session
        pagination: Pagination parameters
        search: Optional search term
        is_active: Optional filter by active status
        _: Current user with required permissions

    Returns:
        PaginatedResponse: List of users with pagination
    """
    # Build filters
    filters = []

    if is_active is not None:
        filters.append(User.is_active == is_active)

    # Add search filter if provided
    if search:
        filters.append(
            or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
        )

    # Apply all filters
    filter_condition = and_(*filters) if filters else None

    # Get users
    users = await user_crud.get_multi(
        db,
        skip=pagination["skip"],
        limit=pagination["limit"],
        filters=[filter_condition] if filter_condition is not None else None,
    )

    # Get total count
    total = await user_crud.get_count(
        db,
        filters=[filter_condition] if filter_condition is not None else None,
    )

    return PaginatedResponse.create(
        items=users,
        total=total,
        page=pagination["page"],
        page_size=pagination["page_size"],
    )


@router.post(
    "/", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permissions(["user:create"])),
) -> Any:
    """
    Create a new user.

    Args:
        user_in: User creation data
        db: Database session
        _: Current user with required permissions

    Returns:
        UserDetailResponse: Created user

    Raises:
        HTTPException: If user already exists
    """
    # Check if user already exists
    existing_user = await user_crud.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create user
    user = await user_crud.create(db, obj_in=user_in)

    # Return user with roles
    return await user_crud.get_user_with_roles(db, user_id=user.id)


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_details(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get details of the current user.

    Args:
        current_user: Current authenticated user

    Returns:
        UserDetailResponse: Current user details
    """
    return current_user


@router.put("/me", response_model=UserDetailResponse)
async def update_current_user(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update current user details.

    Args:
        user_in: User update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        UserDetailResponse: Updated user details

    Raises:
        HTTPException: If email is already taken
    """
    # If changing email, check if new email is already taken
    if user_in.email and user_in.email != current_user.email:
        existing_user = await user_crud.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Don't allow changing superuser status
    if hasattr(user_in, "is_superuser"):
        delattr(user_in, "is_superuser")

    # Update user
    updated_user = await user_crud.update(db, db_obj=current_user, obj_in=user_in)

    return updated_user


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permissions(["user:read"])),
) -> Any:
    """
    Get a specific user by ID.

    Args:
        user_id: User ID
        db: Database session
        _: Current user with required permissions

    Returns:
        UserDetailResponse: User details

    Raises:
        HTTPException: If user not found
    """
    user = await user_crud.get_user_with_roles(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.put("/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permissions(["user:update"])),
) -> Any:
    """
    Update a user.

    Args:
        user_id: User ID
        user_in: User update data
        db: Database session
        _: Current user with required permissions

    Returns:
        UserDetailResponse: Updated user details

    Raises:
        HTTPException: If user not found or email is already taken
    """
    # Get user to update
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # If changing email, check if new email is already taken
    if user_in.email and user_in.email != user.email:
        existing_user = await user_crud.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Update user
    updated_user = await user_crud.update(db, db_obj=user, obj_in=user_in)

    # Return user with roles
    return await user_crud.get_user_with_roles(db, user_id=updated_user.id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permissions(["user:delete"])),
) -> None:
    """
    Delete a user.

    Args:
        user_id: User ID
        db: Database session
        _: Current user with required permissions

    Raises:
        HTTPException: If user not found
    """
    # Get user to delete
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Delete user
    await user_crud.remove(db, id=user_id)


@router.put("/{user_id}/roles", response_model=UserDetailResponse)
async def update_user_roles(
    user_id: str,
    roles_in: UserWithRoles,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> Any:
    """
    Update a user's roles.

    Args:
        user_id: User ID
        roles_in: Roles update data
        db: Database session
        _: Current superuser

    Returns:
        UserDetailResponse: Updated user with roles

    Raises:
        HTTPException: If user not found or roles update fails
    """
    # Update user roles
    updated_user = await user_crud.update_user_roles(
        db,
        user_id=user_id,
        role_ids=roles_in.role_ids,
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return updated_user
