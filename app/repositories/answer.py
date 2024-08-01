from app.models.answer import Answer
from app.utils.repository import SQLAlchemyRepository


class AnswerRepository(SQLAlchemyRepository):
    """
    Repository class for Answer model.

    Inherits from:
        SQLAlchemyRepository: Base class for SQLAlchemy operations.

    Attributes:
        model: The SQLAlchemy model class associated with this repository.
    """
    model = Answer
