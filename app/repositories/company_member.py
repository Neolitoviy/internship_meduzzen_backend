from app.models.company_member import CompanyMember
from app.utils.repository import SQLAlchemyRepository


class CompanyMemberRepository(SQLAlchemyRepository):
    """
    Repository class for CompanyMember model.

    Inherits from:
        SQLAlchemyRepository: Base class for SQLAlchemy operations.

    Attributes:
        model: The SQLAlchemy model class associated with this repository.
    """
    model = CompanyMember
