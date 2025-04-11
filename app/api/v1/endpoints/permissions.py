"""
Permission Endpoints Module

This module defines routes for permission management.
"""
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import parse_pagination_params
from app.core.dependencies import get_current_superuser, require_permissions
from app.crud.permission import permission_crud
from app.db.session import get_db
from app.models.permission import Permission
from app.models.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.permission import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[PermissionResponse])
async def get_permissions(
    db: AsyncSession = Depends(get_db),
    pagination: dict = Depends(parse_pagination_params),
    search: Optional[str] = Query(None, description="Search by name or code"),
    _: User = Depends(require_permissions(["role:read"])),
) -> Any:
    """
    Get all permissions with pagination.

    Args:
        db: Database session
        pagination: Pagination parameters
        search: Optional search term
        _: Current user with required permissions

    Returns:
        PaginatedResponse: List of permissions with pagination
    """
    # Build filters
    filters = []

    # Add search filter if provided
    if search:
        filters.append(
            or_(
                Permission.name.ilike(f"%{search}%"),
                Permission.code.ilike(f"%{search}%"),
            )
        )

    # Apply all filters
    filter_condition = and_(*filters) if filters else None

    # Get permissions
    permissions = await permission_crud.get_multi(
        db,
        skip=pagination["skip"],
        limit=pagination["limit"],
        filters=[filter_condition] if filter_condition is not None else None,
    )

    # Get total count
    total = await permission_crud.get_count(
        db,
        filters=[filter_condition] if filter_condition is not None else None,
    )

    return PaginatedResponse.create(
        items=permissions,
        total=total,
        page=pagination["page"],
        page_size=pagination["page_size"],
    )


@router.post(
    "/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED
)
async def create_permission(
    permission_in: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> Any:
    """
    Create a new permission.

    Args:
        permission_in: Permission creation data
        db: Database session
        _: Current superuser

    Returns:
        PermissionResponse: Created permission

    Raises:
        HTTPException: If permission with the same code already exists
    """
    # Check if permission with this code already exists
    existing_permission = await permission_crud.get_by_code(db, code=permission_in.code)
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Permission with code '{permission_in.code}' already exists",
        )

    # Create permission
    permission = await permission_crud.create(db, obj_in=permission_in)

    return permission


@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permissions(["role:read"])),
) -> Any:
    """
    Get a specific permission by ID.

    Args:
        permission_id: Permission ID
        db: Database session
        _: Current user with required permissions

    Returns:
        PermissionResponse: Permission details

    Raises:
        HTTPException: If permission not found
    """
    permission = await permission_crud.get(db, id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    return permission


@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: str,
    permission_in: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> Any:
    """
    Update a permission.

    Args:
        permission_id: Permission ID
        permission_in: Permission update data
        db: Database session
        _: Current superuser

    Returns:
        PermissionResponse: Updated permission details

    Raises:
        HTTPException: If permission not found
    """
    # Get permission to update
    permission = await permission_crud.get(db, id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    # Update permission
    updated_permission = await permission_crud.update(
        db,
        db_obj=permission,
        obj_in=permission_in,
    )

    return updated_permission


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> None:
    """
    Delete a permission.

    Args:
        permission_id: Permission ID
        db: Database session
        _: Current superuser

    Raises:
        HTTPException: If permission not found
    """
    # Get permission to delete
    permission = await permission_crud.get(db, id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    # Delete permission
    await permission_crud.remove(db, id=permission_id)
