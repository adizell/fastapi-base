# app/main.py

"""
FastAPI Application Entry Point

This module initializes and configures the FastAPI application with all middleware,
exception handlers, and API routers.
"""
import time
from contextlib import asynccontextmanager
from typing import Callable

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router as api_router_v1
from app.core.config import settings
from app.core.exceptions import AppException, handle_app_exception
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle event handler for FastAPI application.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup operations
    if settings.INITIALIZE_DB:
        await init_db()

    yield

    # Shutdown operations
    # Close any connections, etc.


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],  # garante que OPTIONS, POST, GET, etc. sejam aceitos
        allow_headers=["*"],  # permite headers como Authorization, Content-Type, etc.
    )

    # Add API request performance monitoring middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: Callable):
        """
        Middleware to track request processing time.

        Args:
            request: Incoming request
            call_next: Next middleware or route handler

        Returns:
            Response with processing time header
        """
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Set up exception handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """
        Custom exception handler for application specific exceptions.

        Args:
            request: The incoming request
            exc: The raised exception

        Returns:
            JSONResponse with appropriate error information
        """
        return handle_app_exception(exc)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Exception handler for Starlette HTTP exceptions.

        Args:
            request: The incoming request
            exc: The raised exception

        Returns:
            JSONResponse with appropriate error information
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "status_code": exc.status_code},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
            request: Request, exc: RequestValidationError
    ):
        """
        Exception handler for request validation errors.

        Args:
            request: The incoming request
            exc: The raised exception

        Returns:
            JSONResponse with validation error details
        """
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.errors(),
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Validation error",
            },
        )

    # Include API routers
    app.include_router(api_router_v1, prefix=f"{settings.API_PREFIX}/v1")

    return app


app = create_application()

if __name__ == "__main__":
    """Run the application with Uvicorn when script is executed directly."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
