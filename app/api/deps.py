"""
API Dependencies Module

This module defines common FastAPI dependencies for API endpoints.
"""
from typing import Dict, Optional

from fastapi import Depends, Query


async def parse_pagination_params(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> Dict[str, int]:
    """
    Parse and validate pagination parameters.

    Args:
        page: Page number (1-based)
        page_size: Number of items per page

    Returns:
        Dict[str, int]: Pagination parameters with skip, limit, page, and page_size
    """
    return {
        "skip": (page - 1) * page_size,
        "limit": page_size,
        "page": page,
        "page_size": page_size,
    }


async def parse_filtering_params(
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_desc: bool = Query(False, description="Sort in descending order"),
) -> Dict[str, any]:
    """
    Parse and validate filtering parameters.

    Args:
        sort_by: Field to sort by
        sort_desc: Whether to sort in descending order

    Returns:
        Dict[str, any]: Filtering parameters
    """
    return {
        "sort_by": sort_by,
        "sort_desc": sort_desc,
    }
