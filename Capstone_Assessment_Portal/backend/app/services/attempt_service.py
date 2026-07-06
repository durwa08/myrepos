"""
Service layer for quiz attempt management.

Contains the business logic for starting a quiz attempt, including
enforcing the maximum attempts limit and locking a snapshot of the
quiz's questions at the moment the attempt begins.
"""

import logging
from datetime import datetime, timedelta, timezone

from app.constants import MAX_ATTEMPTS_ALLOWED
from app.exceptions.custom_exceptions import (
    MaxAttemptsReachedException,
    QuizNotFoundException,
)
from app.models.attempt_model import AttemptModel
from app.repositories.attempt_repository import (
    count_attempts_by_student_and_quiz,
    create_attempt,
    serialize_attempt,
)
from app.repositories.question_repository import list_questions_by_quiz
from app.repositories.quiz_repository import get_quiz_by_id
from app.schemas.attempt_schema import AttemptResponse

logger = logging.getLogger(__name__)


class AttemptService:
    """Service class for quiz attempt-related business operations."""

    async def start_attempt(self, quiz_id: str, student_id: str) -> AttemptResponse:
        """
        Start a new quiz attempt for a student.

        Validates the quiz exists, enforces the maximum attempts limit,
        and locks a snapshot of the quiz's current questions (including
        correct answers) so later question edits cannot affect this
        attempt's grading.
        """
        quiz = await get_quiz_by_id(quiz_id)
        if quiz is None:
            raise QuizNotFoundException()

        existing_attempts = await count_attempts_by_student_and_quiz(
            student_id, quiz_id
        )
        if existing_attempts >= MAX_ATTEMPTS_ALLOWED:
            raise MaxAttemptsReachedException()

        questions = await list_questions_by_quiz(quiz_id)
        questions_snapshot = [
            {
                "question_id": str(question["_id"]),
                "question_text": question["question_text"],
                "question_type": question["question_type"],
                "options": question["options"],
                "correct_answer_index": question["correct_answer_index"],
                "difficulty": question["difficulty"],
                "tags": question.get("tags", []),
            }
            for question in questions
        ]

        started_at = datetime.now(timezone.utc)
        expires_at = started_at + timedelta(minutes=quiz["time_limit_minutes"])

        new_attempt = AttemptModel(
            quiz_id=quiz_id,
            student_id=student_id,
            attempt_number=existing_attempts + 1,
            questions_snapshot=questions_snapshot,
            started_at=started_at,
            expires_at=expires_at,
        )

        created = await create_attempt(new_attempt)
        logger.info(
            "Attempt started with id=%s for quiz=%s by student=%s (attempt #%s)",
            created["_id"], quiz_id, student_id, new_attempt.attempt_number,
        )

        result = AttemptResponse(**serialize_attempt(created))
        return result