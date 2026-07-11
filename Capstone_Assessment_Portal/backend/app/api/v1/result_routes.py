"""
API routes for viewing quiz results.

Viewing an individual result and personal history is restricted to
students; the admin dashboard is restricted to administrators.
"""

from fastapi import APIRouter, Depends

from app.middleware.auth_middleware import require_admin, require_student
from app.schemas.result_schema import AttemptResultResponse, ResultHistoryItem
from app.services.result_service import ResultService

router = APIRouter(prefix="/results", tags=["Results"])


def get_result_service() -> ResultService:
    """
    Provide a ResultService instance via FastAPI's dependency injection.
    """
    return ResultService()


@router.get("/history/me", response_model=list[ResultHistoryItem])
async def get_my_history(
    current_user: dict = Depends(require_student),
    result_service: ResultService = Depends(get_result_service),
):
    """
    Retrieve the current student's full attempt result history.
    """
    result = await result_service.get_history(student_id=current_user["sub"])
    return result


@router.get("/admin/dashboard", response_model=list[ResultHistoryItem])
async def get_admin_dashboard(
    current_user: dict = Depends(require_admin),
    result_service: ResultService = Depends(get_result_service),
):
    """
    Retrieve every submitted attempt result across all students.

    Only administrators can access this dashboard.
    """
    result = await result_service.get_admin_dashboard()
    return result


@router.get("/{attempt_id}", response_model=AttemptResultResponse)
async def get_attempt_result(
    attempt_id: str,
    current_user: dict = Depends(require_student),
    result_service: ResultService = Depends(get_result_service),
):
    """
    View the result of a submitted attempt.

    Only the student who owns the attempt can view its result.
    """
    result = await result_service.get_result(
        attempt_id, student_id=current_user["sub"]
    )
    return result