import pandas as pd

from app.core.exceptions import BadRequest
from app.schemas.answer import AnswerSchemaCreate
from app.schemas.question import QuestionSchemaCreate
from app.schemas.quiz import CreateQuizRequest


def parse_excel(file_path: str) -> list[CreateQuizRequest]:
    """
    Parses an Excel file to extract quiz data and convert it into a list of CreateQuizRequest objects.

    Args:
        file_path (str): The path to the Excel file containing quiz data.

    Returns:
        list[CreateQuizRequest]: A list of CreateQuizRequest objects created from the Excel file data.

    Raises:
        BadRequest: If the Excel file is missing required columns.
    """
    required_columns = [
        "Quiz Title",
        "Description",
        "Frequency (days)",
        "Company ID",
        "Question Text",
        "Answer Text",
        "Is Correct",
    ]
    df = pd.read_excel(file_path)

    # Check if all required columns are present
    for column in required_columns:
        if column not in df.columns:
            raise BadRequest(f"Missing required column: {column}")

    quizzes = {}

    # Iterate through each row in the DataFrame
    for _, row in df.iterrows():
        quiz_title = row["Quiz Title"]
        description = row["Description"]
        frequency_in_days = row["Frequency (days)"]
        company_id = row["Company ID"]
        question_text = row["Question Text"]
        answer_text = row["Answer Text"]
        is_correct = row["Is Correct"]

        # If quiz title is not in the dictionary, add it
        if quiz_title not in quizzes:
            quizzes[quiz_title] = {
                "title": quiz_title,
                "description": description,
                "frequency_in_days": int(frequency_in_days),
                "questions_data": [],
                "company_id": company_id,
            }

        questions = quizzes[quiz_title]["questions_data"]
        question = next(
            (q for q in questions if q["question_text"] == question_text), None
        )

        # If question text is not in the list of questions, add it
        if question is None:
            question = {"question_text": question_text, "answers": []}
            questions.append(question)

        # Add answer to the question
        question["answers"].append(
            {"answer_text": answer_text, "is_correct": bool(is_correct)}
        )

    # Convert the dictionary of quizzes to a list of CreateQuizRequest objects
    quizzes_list = [
        CreateQuizRequest(
            title=quiz["title"],
            description=quiz["description"],
            frequency_in_days=quiz["frequency_in_days"],
            company_id=quiz["company_id"],
            questions_data=[
                QuestionSchemaCreate(
                    question_text=q["question_text"],
                    answers=[
                        AnswerSchemaCreate(
                            answer_text=a["answer_text"], is_correct=a["is_correct"]
                        )
                        for a in q["answers"]
                    ],
                )
                for q in quiz["questions_data"]
            ],
        )
        for quiz in quizzes.values()
    ]

    return quizzes_list
