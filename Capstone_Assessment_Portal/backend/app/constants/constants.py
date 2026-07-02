from typing import Literal, TypeAlias

ADMIN_ROLE = "admin"
STUDENT_ROLE = "student"

RoleType: TypeAlias = Literal["admin", "student"]

# Category messages
CATEGORY_NOT_FOUND_MESSAGE = "Category not found."
CATEGORY_ALREADY_EXISTS_MESSAGE = "A category with this name already exists."

# Quiz messages
QUIZ_NOT_FOUND_MESSAGE = "Quiz not found."
QUIZ_ALREADY_EXISTS_MESSAGE = (
    "A quiz with this title already exists in the selected category."
)

# Auth messages
INVALID_PASSWORD_MESSAGE = (
    "Password must be at least 8 characters long and include "
    "one uppercase letter, one digit, and one special character."
)