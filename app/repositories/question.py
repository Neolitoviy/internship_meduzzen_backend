from app.models.question import Question
from app.utils.repository import SQLAlchemyRepository


class QuestionRepository(SQLAlchemyRepository):
    """
    Repository class for Question model.

    Inherits from:
        SQLAlchemyRepository: Base class for SQLAlchemy operations.

    Attributes:
        model: The SQLAlchemy model class associated with this repository.
    """
    model = Question
