from typing import List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class PaginationLinks(BaseModel):
    previous: Optional[str]
    next: Optional[str]


class PaginationResponse(BaseModel):
    total_pages: int
    current_page: int
    pagination: PaginationLinks
    items: List[T]

    model_config = {"from_attributes": True}


def paginate(
    items: List[T], total_items: int, skip: int, limit: int, request_url: str
) -> PaginationResponse:
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
