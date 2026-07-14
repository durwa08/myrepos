"""
Service layer for result viewing.

Contains the business logic for viewing a submitted attempt's result,
a student's full result history, and the admin results dashboard.
"""

import logging

from app.exceptions.custom_exceptions import (
    AttemptAccessDeniedException,
    AttemptNotFoundException,
    AttemptNotSubmittedException,
)
from app.repositories.attempt_repository import get_attempt_by_id
from app.repositories.result_repository import (
    list_all_submitted_attempts,
    list_submitted_attempts_by_student,
    serialize_result_summary,
)
from app.schemas.result_schema import (
    AnswerBreakdownItem,
    AttemptResultResponse,
    ResultHistoryItem,
)

logger = logging.getLogger(__name__)


class ResultService:
    """Service class for result-viewing business operations."""

    async def get_result(
        self,
        attempt_id: str,
        student_id: str,
    ) -> AttemptResultResponse:
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
                    options=question["options"],
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

    async def get_history(
        self,
        student_id: str,
    ) -> list[ResultHistoryItem]:
        """
        Retrieve a student's full history of submitted attempt results.
        """
        attempts = await list_submitted_attempts_by_student(student_id)

        result = [
            ResultHistoryItem(**serialize_result_summary(attempt))
            for attempt in attempts
        ]

        return result

    async def get_admin_dashboard(self) -> list[ResultHistoryItem]:
        """
        Retrieve every submitted attempt result across all students.

        Used for the admin results dashboard.
        """
        attempts = await list_all_submitted_attempts()

        result = [
            ResultHistoryItem(**serialize_result_summary(attempt))
            for attempt in attempts
        ]

        return result