"""
API routes for quiz management.

Create, update, and delete operations are restricted to administrators.
Listing and fetching quizzes is available to any authenticated user.
"""

from fastapi import APIRouter, Depends, Query, status

from app.middleware.auth_middleware import get_current_user, require_admin
from app.schemas.quiz_schema import QuizCreateRequest, QuizResponse, QuizUpdateRequest
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])
quiz_service = QuizService()


@router.post("", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    request: QuizCreateRequest,
    current_user: dict = Depends(require_admin),
):
    """
    Create a new quiz.

    Only administrators are authorized to create quizzes.
    """
    result = await quiz_service.create_quiz(request, admin_id=current_user["sub"])
    return result


@router.get("", response_model=list[QuizResponse])
async def list_quizzes(
    category_id: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve all quizzes, optionally filtered by category_id.

    Accessible to any authenticated user.
    """
    result = await quiz_service.get_all_quizzes(category_id)
    return result


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve a single quiz by its id.

    Accessible to any authenticated user.
    """
    result = await quiz_service.get_quiz(quiz_id)
    return result


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: str,
    request: QuizUpdateRequest,
    current_user: dict = Depends(require_admin),
):
    """
    Update an existing quiz.

    Only administrators are authorized to update quizzes.
    """
    result = await quiz_service.update_quiz(quiz_id, request)
    return result


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: str,
    current_user: dict = Depends(require_admin),
):
    """
    Delete a quiz.

    Only administrators are authorized to delete quizzes.
    """
    await quiz_service.delete_quiz(quiz_id)