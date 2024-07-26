from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.utils.pagination import PaginationResponse


class CompanyRequestBase(BaseModel):
    company_id: int


class CompanyRequestCreate(CompanyRequestBase):
    pass


class CompanyRequestResponse(CompanyRequestBase):
    id: int
    requested_user_id: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanyRequestListResponse(PaginationResponse):
    items: List[CompanyRequestResponse]

    model_config = {"from_attributes": True}
