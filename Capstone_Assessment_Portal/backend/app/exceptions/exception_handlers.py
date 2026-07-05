"""
Global exception handlers for the Assessment Portal API.

Maps domain-level exceptions raised in the service layer to proper
HTTP responses, keeping this logic out of main.py.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.constants import (
    CATEGORY_ALREADY_EXISTS_MESSAGE,
    CATEGORY_NOT_FOUND_MESSAGE,
    INVALID_CREDENTIALS_MESSAGE,
    INVALID_REFRESH_TOKEN_MESSAGE,
    QUESTION_ALREADY_EXISTS_MESSAGE,
    QUESTION_NOT_FOUND_MESSAGE,
    QUIZ_ALREADY_EXISTS_MESSAGE,
    QUIZ_NOT_FOUND_MESSAGE,
    USER_ALREADY_EXISTS_MESSAGE,
    USER_NOT_FOUND_MESSAGE,
)
from app.exceptions.custom_exceptions import (
    CategoryAlreadyExistsException,
    CategoryNotFoundException,
    InvalidCredentialsException,
    InvalidRefreshTokenException,
    QuestionAlreadyExistsException,
    QuestionNotFoundException,
    QuizAlreadyExistsException,
    QuizNotFoundException,
    UserAlreadyExistsException,
    UserNotFoundException,
)


async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException):
    """Handle duplicate user registration attempts."""
    return JSONResponse(
        status_code=400,
        content={"detail": USER_ALREADY_EXISTS_MESSAGE},
    )


async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
    """Handle failed login attempts due to bad credentials."""
    return JSONResponse(
        status_code=401,
        content={"detail": INVALID_CREDENTIALS_MESSAGE},
    )


async def invalid_refresh_token_handler(request: Request, exc: InvalidRefreshTokenException):
    """Handle invalid or expired refresh tokens."""
    return JSONResponse(
        status_code=401,
        content={"detail": INVALID_REFRESH_TOKEN_MESSAGE},
    )


async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    """Handle refresh attempts for a user that no longer exists."""
    return JSONResponse(
        status_code=401,
        content={"detail": USER_NOT_FOUND_MESSAGE},
    )


async def category_not_found_handler(request: Request, exc: CategoryNotFoundException):
    """Handle lookups for a category that does not exist."""
    return JSONResponse(
        status_code=404,
        content={"detail": CATEGORY_NOT_FOUND_MESSAGE},
    )


async def category_already_exists_handler(request: Request, exc: CategoryAlreadyExistsException):
    """Handle attempts to create a duplicate category."""
    return JSONResponse(
        status_code=400,
        content={"detail": CATEGORY_ALREADY_EXISTS_MESSAGE},
    )


async def quiz_not_found_handler(request: Request, exc: QuizNotFoundException):
    """Handle lookups for a quiz that does not exist."""
    return JSONResponse(
        status_code=404,
        content={"detail": QUIZ_NOT_FOUND_MESSAGE},
    )


async def quiz_already_exists_handler(request: Request, exc: QuizAlreadyExistsException):
    """Handle attempts to create a duplicate quiz within a category."""
    return JSONResponse(
        status_code=400,
        content={"detail": QUIZ_ALREADY_EXISTS_MESSAGE},
    )


async def question_not_found_handler(request: Request, exc: QuestionNotFoundException):
    """Handle lookups for a question that does not exist."""
    return JSONResponse(
        status_code=404,
        content={"detail": QUESTION_NOT_FOUND_MESSAGE},
    )


async def question_already_exists_handler(request: Request, exc: QuestionAlreadyExistsException):
    """Handle attempts to create a duplicate question within a quiz."""
    return JSONResponse(
        status_code=400,
        content={"detail": QUESTION_ALREADY_EXISTS_MESSAGE},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all custom exception handlers on the given FastAPI app.

    Called once from main.py during application setup, keeping
    exception-to-response mapping logic separate from app wiring.
    """
    app.add_exception_handler(UserAlreadyExistsException, user_already_exists_handler)
    app.add_exception_handler(InvalidCredentialsException, invalid_credentials_handler)
    app.add_exception_handler(InvalidRefreshTokenException, invalid_refresh_token_handler)
    app.add_exception_handler(UserNotFoundException, user_not_found_handler)
    app.add_exception_handler(CategoryNotFoundException, category_not_found_handler)
    app.add_exception_handler(CategoryAlreadyExistsException, category_already_exists_handler)
    app.add_exception_handler(QuizNotFoundException, quiz_not_found_handler)
    app.add_exception_handler(QuizAlreadyExistsException, quiz_already_exists_handler)
    app.add_exception_handler(QuestionNotFoundException, question_not_found_handler)
    app.add_exception_handler(QuestionAlreadyExistsException, question_already_exists_handler)