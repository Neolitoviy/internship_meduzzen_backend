from app.models.company_invitation import CompanyInvitation
from app.utils.repository import SQLAlchemyRepository


class CompanyInvitationRepository(SQLAlchemyRepository):
    model = CompanyInvitation