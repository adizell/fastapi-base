"""
Base Schema Module

This module defines base Pydantic models for schema inheritance.
"""
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing_extensions import Annotated

# Type variable for generic model types
ModelType = TypeVar("ModelType")


class BaseSchema(BaseModel):
    """
    Base schema with common configuration for all Pydantic models.

    Attributes:
        model_config: Configuration options for Pydantic model
    """

    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model -> Pydantic model conversion
        populate_by_name=True,  # Allow populating by field name
        extra="forbid",  # Forbid extra attributes
        str_strip_whitespace=True,  # Strip whitespace from string values
        validate_assignment=True,  # Validate when attributes are assigned
    )


class BaseProperties(BaseSchema):
    """
    Base properties schema with common fields for most models.

    Attributes:
        id: Unique identifier
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: str
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseSchema, Generic[ModelType]):
    """
    Generic schema for paginated responses.

    Attributes:
        items: List of items for the current page
        total: Total number of items
        page: Current page number
        page_size: Number of items per page
        pages: Total number of pages
        has_next: Whether there is a next page
        has_prev: Whether there is a previous page
    """

    items: list[ModelType]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(
        cls,
        items: list[Any],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse":
        """
        Create a paginated response.

        Args:
            items: List of items for the current page
            total: Total number of items
            page: Current page number
            page_size: Number of items per page

        Returns:
            PaginatedResponse: Paginated response object
        """
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )


# Common validators for request parameters
PositiveInt = Annotated[int, Field(gt=0)]

LimitOffset = Annotated[
    Optional[int],
    Field(ge=0, le=1000),
]


class SortQuery(BaseSchema):
    """
    Schema for query sorting parameters.

    Attributes:
        sort_by: Field to sort by
        descending: Sort in descending order
    """

    sort_by: Optional[str] = None
    descending: bool = False

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: Optional[str]) -> Optional[str]:
        """Validate sort_by field."""
        if v and v.startswith("-"):
            return v[1:]
        return v
