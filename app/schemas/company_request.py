from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.utils.pagination import PaginationResponse


class CompanyRequestBase(BaseModel):
    """
    Base model for company request data.
    """
    company_id: int = Field(..., description="ID of the company.")


class CompanyRequestCreate(CompanyRequestBase):
    """
    Model for creating a new company request.

    Inherits:
        CompanyRequestBase: Base model for company request data.
    """
    pass


class CompanyRequestResponse(CompanyRequestBase):
    """
    Model for representing a company request response.
    """
    id: int = Field(..., description="ID of the request.")
    requested_user_id: int = Field(..., description="ID of the user who requested to join the company.")
    status: str = Field(..., description="Status of the request.")
    created_at: datetime = Field(..., description="Timestamp when the request was created.")

    model_config = {"from_attributes": True}


class CompanyRequestListResponse(PaginationResponse):
    """
    Model for paginated list of company requests.
    """
    items: List[CompanyRequestResponse] = Field(..., description="List of company requests.")

    model_config = {"from_attributes": True}
