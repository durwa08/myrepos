"""
Repository layer for question-related database operations.

This module is responsible for all direct interactions with the
questions collection in MongoDB.
"""
import logging
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from app.config.database import get_database
from app.exceptions.custom_exceptions import QuestionAlreadyExistsException
from app.models.question_model import QuestionModel

database = get_database()
question_collection = database["questions"]


async def get_question_by_text_and_quiz(
    question_text: str,
    quiz_id: str,
) -> dict | None:
    """
    Retrieve a question by its text within a specific quiz.

    Used to enforce per-quiz question text uniqueness.
    """
    question = await question_collection.find_one(
        {"question_text": question_text, "quiz_id": quiz_id}
    )
    return question


async def get_question_by_id(question_id: str) -> dict | None:
    """
    Retrieve a question by its MongoDB ObjectId.

    Returns None if the supplied ID is invalid or no question exists.
    """
    question = None

    try:
        obj_id = ObjectId(question_id)
        question = await question_collection.find_one({"_id": obj_id})
    except InvalidId:
        question = None

    return question


async def create_question(question: QuestionModel) -> dict:
    """
    Create a new question and return the saved document.

    Relies on the unique index on (question_text, quiz_id) as a final
    safeguard against duplicate questions created by concurrent requests.
    """
    question_dict = question.model_dump()

    try:
        result = await question_collection.insert_one(question_dict)
    except DuplicateKeyError as exc:
        raise QuestionAlreadyExistsException() from exc

    created_question = await question_collection.find_one(
        {"_id": result.inserted_id}
    )
    return created_question


async def update_question(question_id: str, update_data: dict) -> dict | None:
    """
    Update an existing question with the given fields.

    Returns the updated question, or None if the ID is invalid.
    Relies on the unique index on (question_text, quiz_id) as a final
    safeguard against duplicate questions created by concurrent updates.
    """
    updated_question = None

    try:
        obj_id = ObjectId(question_id)
        await question_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data},
        )
        updated_question = await question_collection.find_one(
            {"_id": obj_id}
        )
    except InvalidId:
        updated_question = None
    except DuplicateKeyError as exc:
        raise QuestionAlreadyExistsException() from exc

    return updated_question


async def delete_question(question_id: str) -> bool:
    """
    Delete a question by its ID.

    Returns True if a question was deleted, otherwise False.
    """
    deleted = False

    try:
        obj_id = ObjectId(question_id)
        result = await question_collection.delete_one({"_id": obj_id})
        deleted = result.deleted_count > 0
    except InvalidId:
        deleted = False

    return deleted


async def list_all_questions() -> list[dict]:
    """
    Retrieve all questions.
    """
    questions = []

    async for question in question_collection.find():
        questions.append(question)

    return questions


async def list_questions_by_quiz(quiz_id: str) -> list[dict]:
    """
    Retrieve all questions belonging to a specific quiz.
    """
    questions = []

    async for question in question_collection.find({"quiz_id": quiz_id}):
        questions.append(question)

    return questions

async def count_questions_by_quiz(quiz_id: str) -> int:
    """
    Count total questions in a quiz.
    """
    try:
        count = await question_collection.count_documents({"quiz_id": quiz_id})
        return count
    except Exception as e:
        logging.error(f"Error counting questions for quiz {quiz_id}: {e}")
        return 0


def serialize_question(question: dict) -> dict:
    """
    Convert a MongoDB question document into an API-friendly format.
    """
    serialized = {
        "id": str(question["_id"]),
        "quiz_id": question["quiz_id"],
        "question_text": question["question_text"],
        "question_type": question["question_type"],
        "options": question["options"],
        "correct_answer_index": question["correct_answer_index"],
        "difficulty": question["difficulty"],
        "tags": question.get("tags", []),
        "created_by": question["created_by"],
    }

    return serialized