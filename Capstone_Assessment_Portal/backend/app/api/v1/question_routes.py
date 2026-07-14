"""
API routes for question management.

Create, update, and delete operations are restricted to administrators.
Listing and fetching questions is available to any authenticated user.
Correct answers are hidden from the student-facing endpoints.
"""

from fastapi import APIRouter, Depends, status

from app.middleware.auth_middleware import (
    get_current_user,
    require_admin,
)
from app.schemas.common_schema import MessageResponse
from app.schemas.question_schema import (
    QuestionCreateRequest,
    QuestionPublicResponse,
    QuestionResponse,
    QuestionUpdateRequest,
)
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])

question_service = QuestionService()


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    request: QuestionCreateRequest,
    current_user: dict = Depends(require_admin),
):
    """
    Create a new question.

    Only administrators are authorized to create questions.
    """
    return await question_service.create_question(
        request,
        admin_id=current_user["sub"],
    )


@router.get(
    "",
    response_model=list[QuestionPublicResponse],
)
async def get_all_questions(
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve all questions.

    Accessible to any authenticated user.
    Correct answers are hidden.
    """
    return await question_service.get_all_questions()


@router.get(
    "/quiz/{quiz_id}",
    response_model=list[QuestionPublicResponse],
)
async def get_questions_by_quiz(
    quiz_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve all questions belonging to a specific quiz.

    Accessible to any authenticated user.
    Correct answers are hidden.
    """
    return await question_service.get_questions_by_quiz(quiz_id)


@router.get(
    "/{question_id}",
    response_model=QuestionPublicResponse,
)
async def get_question(
    question_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve a single question by its id.

    Accessible to any authenticated user.
    Correct answer is hidden.
    """
    return await question_service.get_question(question_id)


@router.put(
    "/{question_id}",
    response_model=QuestionResponse,
)
async def update_question(
    question_id: str,
    request: QuestionUpdateRequest,
    current_user: dict = Depends(require_admin),
):
    """
    Update an existing question.

    Only administrators are authorized to update questions.
    """
    return await question_service.update_question(
        question_id,
        request,
    )


@router.delete(
    "/{question_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_question(
    question_id: str,
    current_user: dict = Depends(require_admin),
):
    """
    Delete a question.

    Only administrators are authorized to delete questions.
    """
    return await question_service.delete_question(question_id)