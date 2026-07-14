"""
Repository layer for result-related database read operations.

This module reads from the same attempts collection as
attempt_repository.py, but is scoped to result viewing: fetching
submitted attempts, student history, and the admin dashboard listing.
"""

from bson import ObjectId
from bson.errors import InvalidId

from app.config.database import get_database

database = get_database()
attempt_collection = database["attempts"]


async def get_submitted_attempt_by_id(attempt_id: str) -> dict | None:
    """
    Retrieve a submitted attempt by its id.

    Returns None if the id is invalid, the attempt doesn't exist,
    or the attempt hasn't been submitted yet.
    """
    attempt = None

    try:
        obj_id = ObjectId(attempt_id)
        attempt = await attempt_collection.find_one(
            {"_id": obj_id, "status": "submitted"}
        )
    except InvalidId:
        attempt = None

    return attempt


async def list_submitted_attempts_by_student(student_id: str) -> list[dict]:
    """
    Retrieve all submitted attempts belonging to a specific student,
    most recent first.
    """
    attempts = []

    cursor = attempt_collection.find(
        {"student_id": student_id, "status": "submitted"}
    ).sort("submitted_at", -1)

    async for attempt in cursor:
        attempts.append(attempt)

    return attempts


async def list_all_submitted_attempts() -> list[dict]:
    """
    Retrieve all submitted attempts across every student, most recent first.

    Used for the admin results dashboard.
    """
    attempts = []

    cursor = attempt_collection.find({"status": "submitted"}).sort(
        "submitted_at", -1
    )

    async for attempt in cursor:
        attempts.append(attempt)

    return attempts


def serialize_result_summary(attempt: dict) -> dict:
    """
    Convert a submitted attempt document into a lightweight result
    summary for history and dashboard listings.
    """
    serialized = {
        "id": str(attempt["_id"]),
        "quiz_id": attempt["quiz_id"],
        "student_id": attempt["student_id"],
        "attempt_number": attempt["attempt_number"],
        "total_questions": attempt["total_questions"],
        "correct_answers": attempt["correct_answers"],
        "percentage": attempt["percentage"],
        "passed": attempt["passed"],
        "submitted_at": attempt["submitted_at"],
    }
    return serialized