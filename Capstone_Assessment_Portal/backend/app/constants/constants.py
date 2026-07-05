from typing import Literal, TypeAlias

ADMIN_ROLE = "admin"
STUDENT_ROLE = "student"

RoleType: TypeAlias = Literal["admin", "student"]

# Auth messages
USER_ALREADY_EXISTS_MESSAGE = "A user with this email already exists."
INVALID_CREDENTIALS_MESSAGE = "Invalid email or password."
INVALID_REFRESH_TOKEN_MESSAGE = "Invalid or expired refresh token."
USER_NOT_FOUND_MESSAGE = "User no longer exists."
CATEGORY_NOT_FOUND_MESSAGE = "Category not found."
CATEGORY_ALREADY_EXISTS_MESSAGE = "A category with this name already exists."


QUIZ_NOT_FOUND_MESSAGE = "Quiz not found."
QUIZ_ALREADY_EXISTS_MESSAGE = (
    "A quiz with this title already exists in the selected category."
)


INVALID_PASSWORD_MESSAGE = (
    "Password must be at least 8 characters long and include "
    "one uppercase letter, one digit, and one special character."
)


QUESTION_NOT_FOUND_MESSAGE = "Question not found."
QUESTION_ALREADY_EXISTS_MESSAGE = (
    "A question with this text already exists in the selected quiz."
)
INVALID_OPTIONS_COUNT_MESSAGE = "MCQ questions must have exactly 4 options."
INVALID_CORRECT_ANSWER_INDEX_MESSAGE = (
    "correct_answer_index is out of range for the given question type."
)