from app.models.company_request import CompanyRequest
from app.utils.repository import SQLAlchemyRepository


class CompanyRequestRepository(SQLAlchemyRepository):
    model = CompanyRequest
