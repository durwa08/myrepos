"""
Service layer for quiz management.

Contains the business logic for creating, retrieving,
updating, and deleting quizzes.
"""

import logging

from app.exceptions.custom_exceptions import (
    CategoryNotFoundException,
    QuizAlreadyExistsException,
    QuizNotFoundException,
)
from app.models.quiz_model import QuizModel
from app.repositories.category_repository import get_category_by_id
from app.repositories.quiz_repository import (
    create_quiz,
    delete_quiz,
    get_quiz_by_id,
    get_quiz_by_title_and_category,
    list_quizzes,
    serialize_quiz,
    update_quiz,
)
from app.schemas.quiz_schema import QuizCreateRequest, QuizResponse, QuizUpdateRequest

logger = logging.getLogger(__name__)


class QuizService:
    """Service class for quiz-related business operations."""

    async def create_quiz(
        self,
        request: QuizCreateRequest,
        admin_id: str,
    ) -> QuizResponse:
        """
        Create a new quiz after validating the category exists and the
        title is unique within that category.
        """
        category = await get_category_by_id(request.category_id)
        if category is None:
            raise CategoryNotFoundException()

        existing = await get_quiz_by_title_and_category(
            request.title, request.category_id
        )
        if existing is not None:
            raise QuizAlreadyExistsException()

        new_quiz = QuizModel(
            title=request.title,
            description=request.description,
            category_id=request.category_id,
            time_limit_minutes=request.time_limit_minutes,
            created_by=admin_id,
        )
        created = await create_quiz(new_quiz)
        logger.info("Quiz created with id=%s by admin=%s", created["_id"], admin_id)

        result = QuizResponse(**serialize_quiz(created))
        return result

    async def get_all_quizzes(self, category_id: str | None = None) -> list[QuizResponse]:
        """
        Retrieve all quizzes, optionally filtered by category.
        """
        quizzes = await list_quizzes(category_id)
        result = [QuizResponse(**serialize_quiz(quiz)) for quiz in quizzes]
        return result

    async def get_quiz(self, quiz_id: str) -> QuizResponse:
        """
        Retrieve a single quiz by its id.
        """
        quiz = await get_quiz_by_id(quiz_id)
        if quiz is None:
            raise QuizNotFoundException()

        result = QuizResponse(**serialize_quiz(quiz))
        return result

    async def update_quiz(
        self,
        quiz_id: str,
        request: QuizUpdateRequest,
    ) -> QuizResponse:
        """
        Update an existing quiz's fields.

        Validates the new category (if changed) and enforces per-category
        title uniqueness (if the title is changed).
        """
        existing = await get_quiz_by_id(quiz_id)
        if existing is None:
            raise QuizNotFoundException()

        update_data = request.model_dump(exclude_unset=True)
        target_category_id = update_data.get("category_id", existing["category_id"])

        if "category_id" in update_data:
            category = await get_category_by_id(update_data["category_id"])
            if category is None:
                raise CategoryNotFoundException()

        if "title" in update_data:
            duplicate = await get_quiz_by_title_and_category(
                update_data["title"], target_category_id
            )
            if duplicate is not None and str(duplicate["_id"]) != quiz_id:
                raise QuizAlreadyExistsException()

        updated = await update_quiz(quiz_id, update_data)
        logger.info("Quiz updated with id=%s", quiz_id)

        result = QuizResponse(**serialize_quiz(updated))
        return result

    async def delete_quiz(self, quiz_id: str) -> None:
        """
        Delete an existing quiz.
        """
        deleted = await delete_quiz(quiz_id)
        if not deleted:
            raise QuizNotFoundException()

        logger.info("Quiz deleted with id=%s", quiz_id)
        result = None
        return result