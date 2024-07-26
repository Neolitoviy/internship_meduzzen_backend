from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.utils.pagination import PaginationResponse


class CompanyInvitationBase(BaseModel):
    company_id: int
    invited_user_id: int

    model_config = {"from_attributes": True}


class CompanyInvitationCreate(CompanyInvitationBase):
    pass


class CompanyInvitationUpdate(CompanyInvitationBase):
    status: Optional[str] = None


class CompanyInvitationResponse(CompanyInvitationBase):
    id: int
    status: Optional[str] = None
    created_at: datetime


class CompanyInvitationListResponse(PaginationResponse):
    items: List[CompanyInvitationResponse]

    model_config = {"from_attributes": True}
