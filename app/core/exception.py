"""
Exceptions Module

This module defines custom application exceptions and handlers.
"""
from typing import Any, Dict, Optional

from fastapi import status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """
    Base application exception class with HTTP status code and detail message.

    Attributes:
        status_code: HTTP status code
        detail: Error detail message
        error_code: Application-specific error code
        headers: Optional HTTP headers to include in response
    """

    def __init__(
            self,
            status_code: int,
            detail: str,
            error_code: Optional[str] = None,
            headers: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize exception with status code, detail message, and optional extras.

        Args:
            status_code: HTTP status code
            detail: Error detail message
            error_code: Application-specific error code
            headers: Optional HTTP headers to include in response
        """
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.headers = headers


class NotFoundError(AppException):
    """
    Exception for resource not found errors (HTTP 404).

    Args:
        detail: Error detail message
        error_code: Application-specific error code
    """

    def __init__(self, detail: str, error_code: Optional[str] = None):
        """Initialize as 404 Not Found with detail message."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
        )


class BadRequestError(AppException):
    """
    Exception for bad request errors (HTTP 400).

    Args:
        detail: Error detail message
        error_code: Application-specific error code
    """

    def __init__(self, detail: str, error_code: Optional[str] = None):
        """Initialize as 400 Bad Request with detail message."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
        )


class UnauthorizedError(AppException):
    """
    Exception for unauthorized errors (HTTP 401).

    Args:
        detail: Error detail message
        error_code: Application-specific error code
    """

    def __init__(self, detail: str = "Not authenticated", error_code: Optional[str] = None):
        """Initialize as 401 Unauthorized with detail message."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(AppException):
    """
    Exception for forbidden errors (HTTP 403).

    Args:
        detail: Error detail message
        error_code: Application-specific error code
    """

    def __init__(self, detail: str = "Insufficient permissions", error_code: Optional[str] = None):
        """Initialize as 403 Forbidden with detail message."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
        )


class ConflictError(AppException):
    """
    Exception for conflict errors (HTTP 409).

    Args:
        detail: Error detail message
        error_code: Application-specific error code
    """

    def __init__(self, detail: str, error_code: Optional[str] = None):
        """Initialize as 409 Conflict with detail message."""
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
        )


class RateLimitError(AppException):
    """
    Exception for rate limit exceeded errors (HTTP 429).

    Args:
        detail: Error detail message
        retry_after: Seconds client should wait before retrying
        error_code: Application-specific error code
    """

    def __init__(
            self,
            detail: str = "Rate limit exceeded",
            retry_after: int = 60,
            error_code: Optional[str] = None
    ):
        """Initialize as 429 Too Many Requests with detail message and Retry-After header."""
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code=error_code,
            headers={"Retry-After": str(retry_after)},
        )


class ServerError(AppException):
    """
    Exception for internal server errors (HTTP 500).

    Args:
        detail: Error detail message
        error_code: Application-specific error code
    """

    def __init__(self, detail: str = "Internal server error", error_code: Optional[str] = None):
        """Initialize as 500 Internal Server Error with detail message."""
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code,
        )


def handle_app_exception(exc: AppException) -> JSONResponse:
    """
    Handle application exceptions by converting them to JSON responses.

    Args:
        exc: Application exception

    Returns:
        JSONResponse with error details
    """
    content = {
        "detail": exc.detail,
        "status_code": exc.status_code,
    }

    if exc.error_code:
        content["error_code"] = exc.error_code

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers,
    )
