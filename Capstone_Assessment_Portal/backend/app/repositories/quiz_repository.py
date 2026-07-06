"""
Repository layer for quiz-related database operations.

This module is responsible for all direct interactions with the
quizzes collection in MongoDB.
"""

from bson import ObjectId
from bson.errors import InvalidId

from app.config.database import get_database
from app.models.quiz_model import QuizModel

database = get_database()
quiz_collection = database["quizzes"]


async def get_quiz_by_title_and_category(title: str, category_id: str) -> dict | None:
    """
    Retrieve a quiz by its title within a specific category.

    Used to enforce per-category title uniqueness.
    """
    quiz = await quiz_collection.find_one(
        {"title": title, "category_id": category_id}
    )
    return quiz


async def get_quiz_by_id(quiz_id: str) -> dict | None:
    """
    Retrieve a quiz by its MongoDB ObjectId.

    Returns None if the supplied ID is invalid or no quiz exists.
    """
    quiz = None

    try:
        obj_id = ObjectId(quiz_id)
        quiz = await quiz_collection.find_one({"_id": obj_id})
    except InvalidId:
        quiz = None

    return quiz


async def create_quiz(quiz: QuizModel) -> dict:
    """
    Create a new quiz and return the saved document.
    """
    quiz_dict = quiz.model_dump(by_alias=True, exclude={"id"})
    result = await quiz_collection.insert_one(quiz_dict)

    created_quiz = await quiz_collection.find_one({"_id": result.inserted_id})
    return created_quiz


async def update_quiz(quiz_id: str, update_data: dict) -> dict | None:
    """
    Update an existing quiz with the given fields.

    Returns the updated quiz, or None if the ID is invalid.
    """
    updated_quiz = None

    try:
        obj_id = ObjectId(quiz_id)
        await quiz_collection.update_one({"_id": obj_id}, {"$set": update_data})
        updated_quiz = await quiz_collection.find_one({"_id": obj_id})
    except InvalidId:
        updated_quiz = None

    return updated_quiz


async def delete_quiz(quiz_id: str) -> bool:
    """
    Delete a quiz by its ID.

    Returns True if a quiz was deleted, otherwise False.
    """
    deleted = False

    try:
        obj_id = ObjectId(quiz_id)
        result = await quiz_collection.delete_one({"_id": obj_id})
        deleted = result.deleted_count > 0
    except InvalidId:
        deleted = False

    return deleted


async def list_quizzes(category_id: str | None = None) -> list[dict]:
    """
    Retrieve all quizzes, optionally filtered by category.
    """
    quizzes = []
    query_filter = {"category_id": category_id} if category_id else {}

    async for quiz in quiz_collection.find(query_filter):
        quizzes.append(quiz)

    return quizzes


def serialize_quiz(quiz: dict) -> dict:
    """
    Convert a MongoDB quiz document into an API-friendly format.
    """
    serialized = {
        "id": str(quiz["_id"]),
        "title": quiz["title"],
        "description": quiz.get("description"),
        "category_id": quiz["category_id"],
        "time_limit_minutes": quiz["time_limit_minutes"],
        "created_by": quiz["created_by"],
    }
    return serialized