"""
Repository layer for quiz attempt database operations.

This module is responsible for all direct interactions with the
attempts collection in MongoDB.
"""

from bson import ObjectId
from bson.errors import InvalidId

from app.config.database import get_database
from app.models.attempt_model import AttemptModel

database = get_database()
attempt_collection = database["attempts"]


async def count_attempts_by_student_and_quiz(student_id: str, quiz_id: str) -> int:
    """
    Count how many attempts a student has already made on a given quiz.

    Used to enforce the maximum allowed attempts per quiz.
    """
    count = await attempt_collection.count_documents(
        {"student_id": student_id, "quiz_id": quiz_id}
    )
    return count


async def get_attempt_by_id(attempt_id: str) -> dict | None:
    """
    Retrieve an attempt by its MongoDB ObjectId.

    Returns None if the supplied ID is invalid or no attempt exists.
    """
    attempt = None

    try:
        obj_id = ObjectId(attempt_id)
        attempt = await attempt_collection.find_one({"_id": obj_id})
    except InvalidId:
        attempt = None

    return attempt


async def create_attempt(attempt: AttemptModel) -> dict:
    """
    Create a new attempt and return the saved document.
    """
    attempt_dict = attempt.model_dump()
    result = await attempt_collection.insert_one(attempt_dict)

    created_attempt = await attempt_collection.find_one({"_id": result.inserted_id})
    return created_attempt


def serialize_attempt(attempt: dict) -> dict:
    """
    Convert a MongoDB attempt document into an API-friendly format.

    Builds the student-safe question list by stripping correct_answer_index
    out of each snapshotted question.
    """
    questions = [
        {
            "question_id": q["question_id"],
            "question_text": q["question_text"],
            "question_type": q["question_type"],
            "options": q["options"],
            "difficulty": q["difficulty"],
            "tags": q.get("tags", []),
        }
        for q in attempt["questions_snapshot"]
    ]

    serialized = {
        "id": str(attempt["_id"]),
        "quiz_id": attempt["quiz_id"],
        "attempt_number": attempt["attempt_number"],
        "status": attempt["status"],
        "started_at": attempt["started_at"],
        "expires_at": attempt["expires_at"],
        "questions": questions,
    }
    return serialized