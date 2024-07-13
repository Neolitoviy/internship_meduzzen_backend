from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class CompanyRequestBase(BaseModel):
    company_id: int


class CompanyRequestCreate(CompanyRequestBase):
    pass


class CompanyRequestResponse(CompanyRequestBase):
    id: int
    requested_user_id: int
    created_at: datetime

    model_config = {
        'from_attributes': True
    }


class PaginationLinks(BaseModel):
    previous: Optional[str] = None
    next: Optional[str] = None


class CompanyRequestListResponse(BaseModel):
    current_page: int
    total_pages: int
    pagination: PaginationLinks
    requests: List[CompanyRequestResponse]

    model_config = {
        'from_attributes': True
    }
