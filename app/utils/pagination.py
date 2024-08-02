from typing import List, Optional, TypeVar

from pydantic import BaseModel

# Type variable for pagination items, must be a subclass of BaseModel
T = TypeVar("T", bound=BaseModel)


class PaginationLinks(BaseModel):
    """
    Model for pagination links.

    Attributes:
        previous (Optional[str]): URL for the previous page, if available.
        next (Optional[str]): URL for the next page, if available.
    """
    previous: Optional[str]
    next: Optional[str]


class PaginationResponse(BaseModel):
    """
    Model for pagination response.

    Attributes:
        total_pages (int): Total number of pages.
        current_page (int): Current page number.
        pagination (PaginationLinks): Links for previous and next pages.
        items (List[T]): List of items for the current page.
    """
    total_pages: int
    current_page: int
    pagination: PaginationLinks
    items: List[T]

    model_config = {"from_attributes": True}


def paginate(
    items: List[T], total_items: int, skip: int, limit: int, request_url: str
) -> PaginationResponse:
    """
    Function to generate a paginated response.

    Args:
        items (List[T]): List of items for the current page.
        total_items (int): Total number of items across all pages.
        skip (int): Number of items to skip.
        limit (int): Maximum number of items per page.
        request_url (str): URL of the current request for pagination links.

    Returns:
        PaginationResponse: Paginated response including items and pagination links.
    """
    total_pages = (total_items + limit - 1) // limit
    current_page = (skip // limit) + 1

    base_url = request_url.split("?")[0]
    previous_page_url = (
        f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}"
        if current_page > 1
        else None
    )
    next_page_url = (
        f"{base_url}?skip={skip + limit}&limit={limit}"
        if current_page < total_pages
        else None
    )

    return PaginationResponse(
        total_pages=total_pages,
        current_page=current_page,
        pagination=PaginationLinks(previous=previous_page_url, next=next_page_url),
        items=items,
    )
