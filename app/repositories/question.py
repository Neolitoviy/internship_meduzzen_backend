from app.models.question import Question
from app.utils.repository import SQLAlchemyRepository


class QuestionRepository(SQLAlchemyRepository):
    model = Question
