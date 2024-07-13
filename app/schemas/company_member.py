from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime


class CompanyMemberBase(BaseModel):
    company_id: int
    user_id: int


class CompanyMemberCreate(CompanyMemberBase):
    ...


class CompanyMemberResponse(CompanyMemberBase):
    id: int
    created_at: datetime

    model_config = {
        'from_attributes': True
    }


class PaginationLinks(BaseModel):
    previous: Optional[str]
    next: Optional[str]


class CompanyMemberListResponse(BaseModel):
    current_page: int
    total_pages: int
    pagination: PaginationLinks
    members: List[CompanyMemberResponse]

    model_config = {
        'from_attributes': True
    }
