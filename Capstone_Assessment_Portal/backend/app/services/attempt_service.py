"""
Service layer for quiz attempt management.

Contains the business logic for starting a quiz attempt, saving
partial answers, resuming an in-progress attempt, submitting an
attempt for scoring, and viewing results.
"""

import logging
from datetime import datetime, timedelta, timezone

from app.constants import (
    ATTEMPT_ACCESS_DENIED_MESSAGE,
    ATTEMPT_EXPIRED_MESSAGE,
    ATTEMPT_NOT_SUBMITTED_MESSAGE,
    INVALID_ANSWER_INDEX_MESSAGE,
    INVALID_QUESTION_FOR_ATTEMPT_MESSAGE,
    MAX_ATTEMPTS_ALLOWED,
)
from app.exceptions.custom_exceptions import (
    AttemptAccessDeniedException,
    AttemptAlreadySubmittedException,
    AttemptExpiredException,
    AttemptNotFoundException,
    AttemptNotSubmittedException,
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
    list_all_submitted_attempts,
    list_submitted_attempts_by_student,
    mark_attempt_expired,
    save_answer,
    serialize_attempt,
    serialize_result_summary,
    submit_attempt,
)
from app.repositories.question_repository import list_questions_by_quiz
from app.repositories.quiz_repository import get_quiz_by_id
from app.schemas.attempt_schema import (
    AnswerBreakdownItem,
    AnswerSaveRequest,
    AttemptResponse,
    AttemptResultResponse,
    ResultHistoryItem,
)

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

    async def submit_attempt(self, attempt_id: str, student_id: str) -> AttemptResultResponse:
        """
        Submit an attempt and compute its score.

        Ownership is verified, but unlike resume/save_answer, an
        expired attempt is still allowed to be submitted (finalizing
        it automatically) rather than being rejected. Already-submitted
        attempts cannot be submitted again.
        """
        attempt = await get_attempt_by_id(attempt_id)
        if attempt is None:
            raise AttemptNotFoundException()

        if attempt["student_id"] != student_id:
            raise AttemptAccessDeniedException()

        if attempt["status"] == "submitted":
            raise AttemptAlreadySubmittedException()

        saved_answers = attempt.get("answers", {})
        questions_snapshot = attempt["questions_snapshot"]

        breakdown = []
        correct_count = 0

        for question in questions_snapshot:
            question_id = question["question_id"]
            selected_index = saved_answers.get(question_id)
            correct_index = question["correct_answer_index"]
            is_correct = selected_index == correct_index

            if is_correct:
                correct_count += 1

            breakdown.append(
                {
                    "question_id": question_id,
                    "question_text": question["question_text"],
                    "selected_answer_index": selected_index,
                    "correct_answer_index": correct_index,
                    "is_correct": is_correct,
                }
            )

        total_questions = len(questions_snapshot)
        percentage = (
            round((correct_count / total_questions) * 100, 2)
            if total_questions > 0
            else 0.0
        )

        quiz = await get_quiz_by_id(attempt["quiz_id"])
        pass_percentage = quiz.get("pass_percentage", 40.0) if quiz else 40.0
        passed = percentage >= pass_percentage

        submission_data = {
            "status": "submitted",
            "submitted_at": datetime.now(timezone.utc),
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "percentage": percentage,
            "passed": passed,
        }

        updated = await submit_attempt(attempt_id, submission_data)
        logger.info(
            "Attempt submitted with id=%s by student=%s, score=%s/%s (%s%%), passed=%s",
            attempt_id, student_id, correct_count, total_questions, percentage, passed,
        )

        result = AttemptResultResponse(
            id=str(updated["_id"]),
            quiz_id=updated["quiz_id"],
            attempt_number=updated["attempt_number"],
            status=updated["status"],
            started_at=updated["started_at"],
            submitted_at=updated["submitted_at"],
            total_questions=updated["total_questions"],
            correct_answers=updated["correct_answers"],
            percentage=updated["percentage"],
            passed=updated["passed"],
            answer_breakdown=[AnswerBreakdownItem(**item) for item in breakdown],
        )
        return result

    async def get_result(self, attempt_id: str, student_id: str) -> AttemptResultResponse:
        """
        Retrieve the result of a submitted attempt.

        Only the student who owns the attempt can view it. Raises if
        the attempt doesn't exist, isn't submitted yet, or belongs to
        a different student.
        """
        attempt = await get_attempt_by_id(attempt_id)
        if attempt is None:
            raise AttemptNotFoundException()

        if attempt["student_id"] != student_id:
            raise AttemptAccessDeniedException()

        if attempt["status"] != "submitted":
            raise AttemptNotSubmittedException()

        breakdown = []
        for question in attempt["questions_snapshot"]:
            question_id = question["question_id"]
            selected_index = attempt.get("answers", {}).get(question_id)
            correct_index = question["correct_answer_index"]
            breakdown.append(
                AnswerBreakdownItem(
                    question_id=question_id,
                    question_text=question["question_text"],
                    selected_answer_index=selected_index,
                    correct_answer_index=correct_index,
                    is_correct=selected_index == correct_index,
                )
            )

        result = AttemptResultResponse(
            id=str(attempt["_id"]),
            quiz_id=attempt["quiz_id"],
            attempt_number=attempt["attempt_number"],
            status=attempt["status"],
            started_at=attempt["started_at"],
            submitted_at=attempt["submitted_at"],
            total_questions=attempt["total_questions"],
            correct_answers=attempt["correct_answers"],
            percentage=attempt["percentage"],
            passed=attempt["passed"],
            answer_breakdown=breakdown,
        )
        return result

    async def get_history(self, student_id: str) -> list[ResultHistoryItem]:
        """
        Retrieve a student's full history of submitted attempt results.
        """
        attempts = await list_submitted_attempts_by_student(student_id)
        result = [
            ResultHistoryItem(**serialize_result_summary(a)) for a in attempts
        ]
        return result

    async def get_admin_dashboard(self) -> list[ResultHistoryItem]:
        """
        Retrieve every submitted attempt result across all students.

        Used for the admin results dashboard.
        """
        attempts = await list_all_submitted_attempts()
        result = [
            ResultHistoryItem(**serialize_result_summary(a)) for a in attempts
        ]
        return result