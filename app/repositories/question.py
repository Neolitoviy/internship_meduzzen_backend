from app.utils.repository import SQLAlchemyRepository
from app.models.question import Question


class QuestionRepository(SQLAlchemyRepository):
    model = Question