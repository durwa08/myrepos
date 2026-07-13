"""
API routes for quiz management.

Create, update, and delete operations are restricted to administrators.
Listing and fetching quizzes is available to any authenticated user.
"""

from fastapi import APIRouter, Depends, Query, status

from app.middleware.auth_middleware import get_current_user, require_admin
from app.schemas.common_schema import MessageResponse
from app.schemas.quiz_schema import QuizCreateRequest, QuizResponse, QuizUpdateRequest
from app.services.quiz_service import QuizService
from app.repositories.question_repository import count_questions_by_quiz

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


def get_quiz_service() -> QuizService:
    """
    Provide a QuizService instance via FastAPI's dependency injection.

    Allows the service to be swapped out in tests using
    app.dependency_overrides, instead of patching the class directly.
    """
    return QuizService()


@router.post("", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    request: QuizCreateRequest,
    current_user: dict = Depends(require_admin),
    quiz_service: QuizService = Depends(get_quiz_service),
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
    quiz_service: QuizService = Depends(get_quiz_service),
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
    quiz_service: QuizService = Depends(get_quiz_service),
):
    """
    Retrieve a single quiz by its id.

    Accessible to any authenticated user.
    """
    result = await quiz_service.get_quiz(quiz_id)
    return result


@router.get("/{quiz_id}/question-count")
async def get_quiz_question_count(
    quiz_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get the number of questions in a quiz."""
    try:
        count = await count_questions_by_quiz(quiz_id)
        return {"quiz_id": quiz_id, "question_count": count}
    except Exception:
        return {"quiz_id": quiz_id, "question_count": 0}


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: str,
    request: QuizUpdateRequest,
    current_user: dict = Depends(require_admin),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    """
    Update an existing quiz.

    Only administrators are authorized to update quizzes.
    """
    result = await quiz_service.update_quiz(quiz_id, request)
    return result


@router.delete("/{quiz_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_quiz(
    quiz_id: str,
    current_user: dict = Depends(require_admin),
    quiz_service: QuizService = Depends(get_quiz_service),
):
    """
    Delete a quiz.

    Only administrators are authorized to delete quizzes.
    """
    result = await quiz_service.delete_quiz(quiz_id)
    return result