"""
Service layer for quiz attempt management.

Contains the business logic for starting a quiz attempt, saving
partial answers, and resuming an in-progress attempt.
"""

import logging
from datetime import datetime, timedelta, timezone

from app.constants import (
    ATTEMPT_ACCESS_DENIED_MESSAGE,
    ATTEMPT_EXPIRED_MESSAGE,
    INVALID_ANSWER_INDEX_MESSAGE,
    INVALID_QUESTION_FOR_ATTEMPT_MESSAGE,
    MAX_ATTEMPTS_ALLOWED,
)
from app.exceptions.custom_exceptions import (
    AttemptAccessDeniedException,
    AttemptExpiredException,
    AttemptNotFoundException,
    InvalidAttemptAnswerException,
    MaxAttemptsReachedException,
    QuizNotFoundException,
)
from app.models.attempt_model import AttemptModel
from app.repositories.attempt_repository import (
    count_attempts_by_student_and_quiz,
    create_attempt,
    get_active_attempt,
    get_attempt_by_id,
    mark_attempt_expired,
    save_answer,
    serialize_attempt,
)
from app.repositories.question_repository import list_questions_by_quiz
from app.repositories.quiz_repository import get_quiz_by_id
from app.schemas.attempt_schema import AnswerSaveRequest, AttemptResponse

logger = logging.getLogger(__name__)


class AttemptService:
    """Service class for quiz attempt-related business operations."""

    async def start_attempt(self, quiz_id: str, student_id: str) -> AttemptResponse:
        """
        Start a new quiz attempt for a student.

        If the student already has an unexpired, in-progress attempt
        for this quiz, that attempt is returned as-is instead of
        creating a new one. If an in-progress attempt has passed its
        time limit, it is marked expired before proceeding.

        Otherwise, validates the quiz exists, enforces the maximum
        attempts limit, and locks a snapshot of the quiz's current
        questions (including correct answers) so later question edits
        cannot affect this attempt's grading.
        """
        quiz = await get_quiz_by_id(quiz_id)
        if quiz is None:
            raise QuizNotFoundException()

        active_attempt = await get_active_attempt(student_id, quiz_id)
        if active_attempt is not None:
            now = datetime.now(timezone.utc)
            expires_at = active_attempt["expires_at"]
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if now <= expires_at:
                result = AttemptResponse(**serialize_attempt(active_attempt))
                return result

            await mark_attempt_expired(str(active_attempt["_id"]))

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
    


    async def _get_valid_attempt(self, attempt_id: str, student_id: str) -> dict:
        """
        Fetch an attempt, verify ownership, and check it hasn't expired.

        Automatically marks the attempt as expired in the database if
        its time limit has passed but it hasn't been flagged yet.
        Returns the raw attempt document for further processing.
        """
        attempt = await get_attempt_by_id(attempt_id)
        if attempt is None:
            raise AttemptNotFoundException()

        if attempt["student_id"] != student_id:
            raise AttemptAccessDeniedException()

        now = datetime.now(timezone.utc)
        expires_at = attempt["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if attempt["status"] == "expired" or now > expires_at:
            if attempt["status"] != "expired":
                await mark_attempt_expired(attempt_id)
            raise AttemptExpiredException()

        return attempt

    async def resume_attempt(self, attempt_id: str, student_id: str) -> AttemptResponse:
        """
        Resume an in-progress attempt, returning its current state
        including any previously saved answers.
        """
        attempt = await self._get_valid_attempt(attempt_id, student_id)
        result = AttemptResponse(**serialize_attempt(attempt))
        return result

    async def save_answer(
        self,
        attempt_id: str,
        request: AnswerSaveRequest,
        student_id: str,
    ) -> AttemptResponse:
        """
        Save a single answer for a question within an in-progress attempt.

        Validates that the question belongs to this attempt's locked
        snapshot and that the answer index is within range for that
        question's options.
        """
        attempt = await self._get_valid_attempt(attempt_id, student_id)

        snapshot_question = next(
            (
                q for q in attempt["questions_snapshot"]
                if q["question_id"] == request.question_id
            ),
            None,
        )
        if snapshot_question is None:
            raise InvalidAttemptAnswerException(INVALID_QUESTION_FOR_ATTEMPT_MESSAGE)

        if not 0 <= request.answer_index < len(snapshot_question["options"]):
            raise InvalidAttemptAnswerException(INVALID_ANSWER_INDEX_MESSAGE)

        updated = await save_answer(attempt_id, request.question_id, request.answer_index)
        logger.info(
            "Answer saved for attempt=%s question=%s by student=%s",
            attempt_id, request.question_id, student_id,
        )

        result = AttemptResponse(**serialize_attempt(updated))
        return result