"""
Role Endpoints Module

This module defines routes for role management.
"""
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import parse_pagination_params
from app.core.dependencies import require_permissions
from app.crud.role import role_crud
from app.db.session import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.role import (
    RoleCreate,
    RoleDetailResponse,
    RoleResponse,
    RoleUpdate,
    RoleWithPermissions,
)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[RoleResponse])
async def get_roles(
    db: AsyncSession = Depends(get_db),
    pagination: dict = Depends(parse_pagination_params),
    search: Optional[str] = Query(None, description="Search by name or code"),
    _: User = Depends(require_permissions(["role:read"])),
) -> Any:
    """
    Get all roles with pagination.

    Args:
        db: Database session
        pagination: Pagination parameters
        search: Optional search term
        _: Current user with required permissions

    Returns:
        PaginatedResponse: List of roles with pagination
    """
    # Build filters
    filters = []

    # Add search filter if provided
    if search:
        filters.append(
            or_(
                Role.name.ilike(f"%{search}%"),
                Role.code.ilike(f"%{search}%"),
            )
        )

    # Apply all filters
    filter_condition = and_(*filters) if filters else None

    # Get roles
    roles = await role_crud.get_multi(
        db,
        skip=pagination["skip"],
        limit=pagination["limit"],
        filters=[filter_condition] if filter_condition is not None else None,
    )

    # Get total count
    total = await role_crud.get_count(
        db,
        filters=[filter_condition] if filter_condition is not None else None,
    )

    return PaginatedResponse.create(
        items=roles,
        total=total,
        page=pagination["page"],
        page_size=pagination["page_size"],
    )


@router.post(
    "/", response_model=RoleDetailResponse, status_code=status.HTTP_201_CREATED
)
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permissions(["role:create"])),
) -> Any:
    """
    Create a new role.

    Args:
        role_in: Role creation data
        db: Database session
        _: Current user with required permissions

    Returns:
        RoleDetailResponse: Created role

    Raises:
        HTTPException: If role with the same code already exists
    """
    # Check if role with this code already exists
    existing_role = await role_crud.get_by_code(db, code=role_in.code)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with code '{role_in.code}' already exists",
        )

    # Create role
    role = await role_crud.create(db, obj_in=role_in)

    # Return role with permissions
    return await role_crud.get_with_permissions(db, role_id=role.id)


@router.get("/{role_id}", response_model=RoleDetailResponse)
async def get_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permissions(["role:read"])),
) -> Any:
    """
    Get a specific role by ID.

    Args:
        role_id: Role ID
        db: Database session
        _: Current user with required permissions

    Returns:
        RoleDetailResponse: Role details

    Raises:
        HTTPException: If role not found
    """
    role = await role_crud.get_with_permissions(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return role


@router.put("/{role_id}", response_model=RoleDetailResponse)
async def update_role(
    role_id: str,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permissions(["role:update"])),
) -> Any:
    """
    Update a role.

    Args:
        role_id: Role ID
        role_in: Role update data
        db: Database session
        _: Current user with required permissions

    Returns:
        RoleDetailResponse: Updated role details

    Raises:
        HTTPException: If role not found
    """
    # Get role to update
    role = await role_crud.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Update role
    updated_role = await role_crud.update(db, db_obj=role, obj_in=role_in)

    # Return role with permissions
    return await role_crud.get_with_permissions(db, role_id=updated_role.id)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permissions(["role:delete"])),
) -> None:
    """
    Delete a role.

    Args:
        role_id: Role ID
        db: Database session
        _: Current user with required permissions

    Raises:
        HTTPException: If role not found
    """
    # Get role to delete
    role = await role_crud.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Delete role
    await role_crud.remove(db, id=role_id)


@router.put("/{role_id}/permissions", response_model=RoleDetailResponse)
async def update_role_permissions(
    role_id: str,
    permissions_in: RoleWithPermissions,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permissions(["role:update"])),
) -> Any:
    """
    Update a role's permissions.

    Args:
        role_id: Role ID
        permissions_in: Permissions update data
        db: Database session
        _: Current user with required permissions

    Returns:
        RoleDetailResponse: Updated role with permissions

    Raises:
        HTTPException: If role not found or permissions update fails
    """
    # Update role permissions
    updated_role = await role_crud.update_role_permissions(
        db,
        role_id=role_id,
        permission_ids=permissions_in.permission_ids,
    )

    if not updated_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return updated_role
