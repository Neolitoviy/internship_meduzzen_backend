from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.utils.pagination import PaginationResponse


class CompanyInvitationBase(BaseModel):
    """
    Base class for company invitation schema.
    """
    company_id: int = Field(..., description="The ID of the company.")
    invited_user_id: int = Field(..., description="The ID of the invited user.")

    model_config = {"from_attributes": True}


class CompanyInvitationCreate(CompanyInvitationBase):
    """
    Schema for creating a company invitation.
    """
    pass


class CompanyInvitationUpdate(CompanyInvitationBase):
    """
    Schema for updating a company invitation.
    """
    status: Optional[str] = Field(None, description="The status of the invitation.")


class CompanyInvitationResponse(CompanyInvitationBase):
    """
    Schema for the response of a company invitation.
    """
    id: int = Field(..., description="The ID of the invitation.")
    status: Optional[str] = Field(None, description="The status of the invitation.")
    created_at: datetime = Field(..., description="The creation timestamp of the invitation.")


class CompanyInvitationListResponse(PaginationResponse):
    """
    Schema for a paginated list of company invitations.
    """
    items: List[CompanyInvitationResponse] = Field(..., description="The list of company invitations.")

    model_config = {"from_attributes": True}
