"""
API Router Module

This module configures the main API router and includes all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, roles, permissions

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])

# Add more endpoint routers here as needed
