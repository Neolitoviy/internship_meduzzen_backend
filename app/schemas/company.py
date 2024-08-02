from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.utils.pagination import PaginationResponse


class CompanyBase(BaseModel):
    """
    Base model for a company.
    """
    name: str = Field(..., description="The name of the company.")
    description: Optional[str] = Field(None, description="A description of the company.")
    visibility: Optional[bool] = Field(True, description="The visibility status of the company.")

    model_config = {"from_attributes": True}


class CompanyCreate(CompanyBase):
    """
    Model for creating a company.
    """
    pass


class CompanyUpdate(CompanyBase):
    """
    Model for updating a company.
    """
    name: Optional[str] = Field(None, description="The updated name of the company.")
    visibility: Optional[bool] = Field(None, description="The updated visibility status of the company.")


class CompanyInDB(CompanyBase):
    """
    Model for a company in the database.
    """
    id: int = Field(..., description="The unique identifier of the company.")
    owner_id: int = Field(..., description="The unique identifier of the owner of the company.")
    created_at: datetime = Field(..., description="The date and time when the company was created.")
    updated_at: datetime = Field(..., description="The date and time when the company was last updated.")

    model_config = {"from_attributes": True}


class CompanyResponse(CompanyInDB):
    """
    Model for the response of a company.

    Inherits all attributes from CompanyInDB.
    """
    pass


class CompanyListResponse(PaginationResponse):
    """
    Model for the response of a list of companies with pagination.
    """
    items: List[CompanyResponse] = Field(..., description="The list of company responses.")

    model_config = {"from_attributes": True}
