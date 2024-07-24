from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    visibility: Optional[bool] = True

    model_config = {"from_attributes": True}


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    name: Optional[str] = None
    visibility: Optional[bool] = None


class CompanyInDB(CompanyBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyResponse(CompanyInDB):
    pass


class PaginationLinks(BaseModel):
    previous: Optional[str]
    next: Optional[str]


class CompanyListResponse(BaseModel):
    total_pages: int
    current_page: int
    pagination: PaginationLinks
    companies: List[CompanyResponse]
