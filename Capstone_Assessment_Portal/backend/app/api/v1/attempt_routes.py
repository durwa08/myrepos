"""
API routes for quiz attempts.

Starting an attempt is restricted to students, since only candidates
take quizzes in this system.
"""

from fastapi import APIRouter, Depends, status

from app.middleware.auth_middleware import require_student
from app.schemas.attempt_schema import AttemptResponse
from app.services.attempt_service import AttemptService

router = APIRouter(prefix="/attempts", tags=["Attempts"])
attempt_service = AttemptService()


@router.post(
    "/start/{quiz_id}",
    response_model=AttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_attempt(
    quiz_id: str,
    current_user: dict = Depends(require_student),
):
    """
    Start a new quiz attempt.

    Only students are authorized to attempt quizzes. Enforces the
    maximum allowed attempts per quiz and locks a snapshot of the
    quiz's questions at this moment.
    """
    result = await attempt_service.start_attempt(
        quiz_id, student_id=current_user["sub"]
    )
    return result