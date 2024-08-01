from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.utils.pagination import PaginationResponse


class CompanyMemberBase(BaseModel):
    """
    Base model for company members.
    """
    company_id: int = Field(..., description="ID of the company.")
    user_id: int = Field(..., description="ID of the user.")
    is_admin: bool = Field(..., description="Indicates if the user is an admin of the company.")


class CompanyMemberResponse(CompanyMemberBase):
    """
    Response model for a company member.

    Inherits from CompanyMemberBase and adds additional attributes.
    """
    id: int = Field(..., description="ID of the company member.")
    created_at: datetime = Field(..., description="Timestamp when the member was added.")

    model_config = {"from_attributes": True}


class CompanyMemberListResponse(PaginationResponse):
    """
    Paginated response model for a list of company members.

    Inherits from PaginationResponse and adds a list of company member responses.
    """
    items: List[CompanyMemberResponse] = Field(..., description="List of company member responses.")

    model_config = {"from_attributes": True}
