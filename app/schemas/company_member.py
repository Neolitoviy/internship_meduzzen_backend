from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.utils.pagination import PaginationResponse


class CompanyMemberBase(BaseModel):
    company_id: int
    user_id: int
    is_admin: bool


class CompanyMemberResponse(CompanyMemberBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanyMemberListResponse(PaginationResponse):
    items: List[CompanyMemberResponse]

    model_config = {"from_attributes": True}
