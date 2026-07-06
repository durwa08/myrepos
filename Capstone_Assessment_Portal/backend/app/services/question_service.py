"""
Service layer for question management.

Contains the business logic for creating, retrieving, updating,
and deleting questions.
"""

import logging

from app.constants import (
    INVALID_CORRECT_ANSWER_INDEX_MESSAGE,
    INVALID_OPTIONS_COUNT_MESSAGE,
    MCQ_OPTIONS_COUNT,
    TRUE_FALSE_OPTIONS,
)

from app.exceptions.custom_exceptions import (
    QuestionAlreadyExistsException,
    QuestionNotFoundException,
    QuizNotFoundException,
)
from app.models.question_model import QuestionModel
from app.repositories.quiz_repository import get_quiz_by_id
from app.repositories.question_repository import (
    create_question,
    delete_question,
    get_question_by_id,
    get_question_by_text_and_quiz,
    list_questions_by_quiz,
    serialize_question,
    update_question,
)
from app.schemas.question_schema import (
    QuestionCreateRequest,
    QuestionResponse,
    QuestionUpdateRequest,
)

logger = logging.getLogger(__name__)




class QuestionService:
    """Service class for question-related business operations."""

    async def create_question(
        self,
        request: QuestionCreateRequest,
        admin_id: str,
    ) -> QuestionResponse:
        """
        Create a new question after validating the quiz exists and the
        question text is unique within that quiz.
        """
        quiz = await get_quiz_by_id(request.quiz_id)
        if quiz is None:
            raise QuizNotFoundException()

        existing = await get_question_by_text_and_quiz(
            request.question_text, request.quiz_id
        )
        if existing is not None:
            raise QuestionAlreadyExistsException()

        new_question = QuestionModel(
            quiz_id=request.quiz_id,
            question_text=request.question_text,
            question_type=request.question_type,
            options=request.options,
            correct_answer_index=request.correct_answer_index,
            difficulty=request.difficulty,
            tags=request.tags,
            created_by=admin_id,
        )
        created = await create_question(new_question)
        logger.info(
            "Question created with id=%s for quiz=%s by admin=%s",
            created["_id"], request.quiz_id, admin_id,
        )

        result = QuestionResponse(**serialize_question(created))
        return result

    async def get_questions_by_quiz(self, quiz_id: str) -> list[QuestionResponse]:
        """
        Retrieve all questions belonging to a quiz.

        Validates that the quiz itself exists first.
        """
        quiz = await get_quiz_by_id(quiz_id)
        if quiz is None:
            raise QuizNotFoundException()

        questions = await list_questions_by_quiz(quiz_id)
        result = [QuestionResponse(**serialize_question(q)) for q in questions]
        return result

    async def get_question(self, question_id: str) -> QuestionResponse:
        """
        Retrieve a single question by its id.
        """
        question = await get_question_by_id(question_id)
        if question is None:
            raise QuestionNotFoundException()

        result = QuestionResponse(**serialize_question(question))
        return result

    async def update_question(
        self,
        question_id: str,
        request: QuestionUpdateRequest,
    ) -> QuestionResponse:
        """
        Update an existing question's fields.

        Re-validates options/correct_answer_index consistency against
        the merged (existing + incoming) state, since a partial update
        may only touch one of these interdependent fields.
        """
        existing = await get_question_by_id(question_id)
        if existing is None:
            raise QuestionNotFoundException()

        update_data = request.model_dump(exclude_unset=True)

        merged_type = update_data.get("question_type", existing["question_type"])
        merged_options = update_data.get("options", existing["options"])
        merged_index = update_data.get(
            "correct_answer_index", existing["correct_answer_index"]
        )

        if merged_type == "mcq":
            if merged_options is None or len(merged_options) != MCQ_OPTIONS_COUNT:
                raise ValueError(INVALID_OPTIONS_COUNT_MESSAGE)
            if not 0 <= merged_index < MCQ_OPTIONS_COUNT:
                raise ValueError(INVALID_CORRECT_ANSWER_INDEX_MESSAGE)

        if merged_type == "true_false":
            merged_options = TRUE_FALSE_OPTIONS
            update_data["options"] = TRUE_FALSE_OPTIONS
            if not 0 <= merged_index < len(TRUE_FALSE_OPTIONS):
                raise ValueError(INVALID_CORRECT_ANSWER_INDEX_MESSAGE)

        if "question_text" in update_data:
            duplicate = await get_question_by_text_and_quiz(
                update_data["question_text"], existing["quiz_id"]
            )
            if duplicate is not None and str(duplicate["_id"]) != question_id:
                raise QuestionAlreadyExistsException()

        updated = await update_question(question_id, update_data)
        logger.info("Question updated with id=%s", question_id)

        result = QuestionResponse(**serialize_question(updated))
        return result

    async def delete_question(self, question_id: str) -> None:
        """
        Delete an existing question.
        """
        deleted = await delete_question(question_id)
        if not deleted:
            raise QuestionNotFoundException()

        logger.info("Question deleted with id=%s", question_id)
        result = None
        return result