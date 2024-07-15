from app.models.quiz import Quiz
from app.utils.repository import SQLAlchemyRepository


class QuizRepository(SQLAlchemyRepository):
    model = Quiz
