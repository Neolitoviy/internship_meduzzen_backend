from app.utils.repository import SQLAlchemyRepository
from app.models.answer import Answer


class AnswerRepository(SQLAlchemyRepository):
    model = Answer