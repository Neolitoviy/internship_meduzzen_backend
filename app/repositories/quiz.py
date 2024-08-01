from app.models.quiz import Quiz
from app.utils.repository import SQLAlchemyRepository


class QuizRepository(SQLAlchemyRepository):
    """
    Repository class for Quiz model.

    Inherits from:
        SQLAlchemyRepository: Base class for SQLAlchemy operations.

    Attributes:
        model: The SQLAlchemy model class associated with this repository.
    """
    model = Quiz
