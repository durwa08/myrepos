from typing import Literal, TypeAlias

ADMIN_ROLE = "admin"
STUDENT_ROLE = "student"

RoleType: TypeAlias = Literal["admin", "student"]

USER_ALREADY_EXISTS_MESSAGE = "A user with this email already exists."
INVALID_CREDENTIALS_MESSAGE = "Invalid email or password."
INVALID_REFRESH_TOKEN_MESSAGE = "Invalid or expired refresh token."
USER_NOT_FOUND_MESSAGE = "User no longer exists."
INVALID_PASSWORD_MESSAGE = (
    "Password must be at least 8 characters long and include "
    "one uppercase letter, one digit, and one special character."
)

# Category messages
CATEGORY_NOT_FOUND_MESSAGE = "Category not found."
CATEGORY_ALREADY_EXISTS_MESSAGE = "A category with this name already exists."
CATEGORY_DELETED_MESSAGE = "Category deleted successfully."

# Quiz messages
QUIZ_NOT_FOUND_MESSAGE = "Quiz not found."
QUIZ_ALREADY_EXISTS_MESSAGE = (
    "A quiz with this title already exists in the selected category."
)
QUIZ_DELETED_MESSAGE = "Quiz deleted successfully."

# Question messages
QUESTION_NOT_FOUND_MESSAGE = "Question not found."
QUESTION_ALREADY_EXISTS_MESSAGE = (
    "A question with this text already exists in the selected quiz."
)
QUESTION_DELETED_MESSAGE = "Question deleted successfully."
INVALID_OPTIONS_COUNT_MESSAGE = "MCQ questions must have exactly 4 options."
INVALID_CORRECT_ANSWER_INDEX_MESSAGE = (
    "correct_answer_index is out of range for the given question type."
)

MCQ_OPTIONS_COUNT = 4
TRUE_FALSE_OPTIONS = ["True", "False"]

ATTEMPT_NOT_FOUND_MESSAGE = "Attempt not found."
MAX_ATTEMPTS_REACHED_MESSAGE = "Maximum number of attempts reached for this quiz."
MAX_ATTEMPTS_ALLOWED = 3


ATTEMPT_EXPIRED_MESSAGE = "This attempt has expired."
ATTEMPT_ACCESS_DENIED_MESSAGE = "You are not authorized to access this attempt."
INVALID_QUESTION_FOR_ATTEMPT_MESSAGE = "This question does not belong to the current attempt."
INVALID_ANSWER_INDEX_MESSAGE = "answer_index is out of range for this question's options."