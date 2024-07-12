from app.models.company import Company
from app.utils.repository import SQLAlchemyRepository


class CompanyRepository(SQLAlchemyRepository):
    model = Company
