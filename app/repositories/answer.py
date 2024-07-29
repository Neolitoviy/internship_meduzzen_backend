from app.models.answer import Answer
from app.utils.repository import SQLAlchemyRepository


class AnswerRepository(SQLAlchemyRepository):
    model = Answer
