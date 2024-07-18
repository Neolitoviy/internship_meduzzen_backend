from app.models.company_member import CompanyMember
from app.utils.repository import SQLAlchemyRepository


class CompanyMemberRepository(SQLAlchemyRepository):
    model = CompanyMember