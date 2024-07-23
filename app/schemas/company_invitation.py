from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime


class CompanyInvitationBase(BaseModel):
    company_id: int
    invited_user_id: int

    model_config = {
        'from_attributes': True
    }


class CompanyInvitationCreate(CompanyInvitationBase):
    pass


class CompanyInvitationUpdate(CompanyInvitationBase):
    status: Optional[str] = None


class CompanyInvitationResponse(CompanyInvitationBase):
    id: int
    status: Optional[str] = None
    created_at: datetime


class PaginationLinks(BaseModel):
    previous: Optional[str]
    next: Optional[str]


class CompanyInvitationListResponse(BaseModel):
    current_page: int
    total_pages: int
    pagination: PaginationLinks
    invitations: List[CompanyInvitationResponse]

    model_config = {
        'from_attributes': True
    }
