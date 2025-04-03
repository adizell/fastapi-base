"""
Authentication Endpoints Module

This module defines authentication routes for login, token refresh, and related operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.db.session import get_db
from app.schemas.token import RefreshToken, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import auth_service
from app.crud.user import user_crud

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db),
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.

    Args:
        form_data: OAuth2 password request form
        db: Database session

    Returns:
        Token: Access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    user = await auth_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return await auth_service.create_tokens(user)


@router.post("/refresh", response_model=Token)
async def refresh_token(
        token_data: RefreshToken,
        db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Refresh access token using a valid refresh token.

    Args:
        token_data: Refresh token data
        db: Database session

    Returns:
        Token: New access and refresh tokens

    Raises:
        UnauthorizedError: If refresh token is invalid
    """
    try:
        return await auth_service.refresh_token(db, token_data.refresh_token)
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Register a new user.

    Args:
        user_in: User creation data
        db: Database session

    Returns:
        UserResponse: Created user

    Raises:
        HTTPException: If email already exists
    """
    # Check if user with this email already exists
    user = await user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create regular user (not superuser)
    user_in.is_superuser = False

    # Create new user
    user = await user_crud.create(db, obj_in=user_in)

    # Assign default roles if needed
    # This could be extended to automatically assign a default role

    return user
