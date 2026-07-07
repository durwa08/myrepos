"""
API routes for quiz attempts.

Starting an attempt is restricted to students, since only candidates
take quizzes in this system.
"""

from fastapi import APIRouter, Depends, status

from app.middleware.auth_middleware import require_student
from app.schemas.attempt_schema import AnswerSaveRequest, AttemptResponse, AttemptResultResponse
from app.services.attempt_service import AttemptService

router = APIRouter(prefix="/attempts", tags=["Attempts"])


def get_attempt_service() -> AttemptService:
    """
    Provide an AttemptService instance via FastAPI's dependency injection.

    Allows the service to be swapped out in tests using
    app.dependency_overrides, instead of patching the class directly.
    """
    return AttemptService()


@router.post(
    "/start/{quiz_id}",
    response_model=AttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_attempt(
    quiz_id: str,
    current_user: dict = Depends(require_student),
    attempt_service: AttemptService = Depends(get_attempt_service),
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

@router.get("/{attempt_id}", response_model=AttemptResponse)
async def resume_attempt(
    attempt_id: str,
    current_user: dict = Depends(require_student),
    attempt_service: AttemptService = Depends(get_attempt_service),
):
    """
    Resume an in-progress attempt.

    Only the student who owns the attempt can access it. Attempts
    past their time limit are rejected and marked expired.
    """
    result = await attempt_service.resume_attempt(
        attempt_id, student_id=current_user["sub"]
    )
    return result

@router.patch("/{attempt_id}/answers", response_model=AttemptResponse)
async def save_answer(
    attempt_id: str,
    request: AnswerSaveRequest,
    current_user: dict = Depends(require_student),
    attempt_service: AttemptService = Depends(get_attempt_service),
):
    """
    Save a single answer for a question within an in-progress attempt.

    Only the student who owns the attempt can save answers to it.
    """
    result = await attempt_service.save_answer(
        attempt_id, request, student_id=current_user["sub"]
    )
    return result

@router.post("/{attempt_id}/submit", response_model=AttemptResultResponse)
async def submit_attempt(
    attempt_id: str,
    current_user: dict = Depends(require_student),
    attempt_service: AttemptService = Depends(get_attempt_service),
):
    """
    Submit an attempt and receive the computed score and breakdown.

    Only the student who owns the attempt can submit it. Expired
    attempts can still be submitted; already-submitted attempts cannot.
    """
    result = await attempt_service.submit_attempt(
        attempt_id, student_id=current_user["sub"]
    )
    return result