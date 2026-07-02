"""
Application entry point for the Assessment Portal API.

Registers routers and global exception handlers that map domain
exceptions raised in the service layer to proper HTTP responses.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.auth_routes import router as auth_router
from app.api.v1.category_routes import router as category_router
from app.api.v1.quiz_routes import router as quiz_router
from app.config.database import init_indexes
from app.constants.constants import (
    CATEGORY_ALREADY_EXISTS_MESSAGE,
    CATEGORY_NOT_FOUND_MESSAGE,
    QUIZ_ALREADY_EXISTS_MESSAGE,
    QUIZ_NOT_FOUND_MESSAGE,
)
from app.exceptions.custom_exceptions import (
    CategoryAlreadyExistsException,
    CategoryNotFoundException,
    InvalidCredentialsException,
    InvalidRefreshTokenException,
    QuizAlreadyExistsException,
    QuizNotFoundException,
    UserAlreadyExistsException,
    UserNotFoundException,
)

app = FastAPI(
    title="Assessment Portal API",
    description="Backend APIs for the Assessment Portal capstone project",
    version="1.0.0",
)


@app.on_event("startup")
async def on_startup():
    """
    Run initialization tasks when the application starts.
    """
    await init_indexes()


@app.exception_handler(UserAlreadyExistsException)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException):
    """Handle duplicate user registration attempts."""
    return JSONResponse(
        status_code=400,
        content={"detail": "A user with this email already exists."},
    )


@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
    """Handle failed login attempts due to bad credentials."""
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid email or password."},
    )


@app.exception_handler(InvalidRefreshTokenException)
async def invalid_refresh_token_handler(request: Request, exc: InvalidRefreshTokenException):
    """Handle invalid or expired refresh tokens."""
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid or expired refresh token."},
    )


@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    """Handle refresh attempts for a user that no longer exists."""
    return JSONResponse(
        status_code=401,
        content={"detail": "User no longer exists."},
    )


@app.exception_handler(CategoryNotFoundException)
async def category_not_found_handler(request: Request, exc: CategoryNotFoundException):
    """Handle lookups for a category that does not exist."""
    return JSONResponse(
        status_code=404,
        content={"detail": CATEGORY_NOT_FOUND_MESSAGE},
    )


@app.exception_handler(CategoryAlreadyExistsException)
async def category_already_exists_handler(request: Request, exc: CategoryAlreadyExistsException):
    """Handle attempts to create a duplicate category."""
    return JSONResponse(
        status_code=400,
        content={"detail": CATEGORY_ALREADY_EXISTS_MESSAGE},
    )


@app.exception_handler(QuizNotFoundException)
async def quiz_not_found_handler(request: Request, exc: QuizNotFoundException):
    """Handle lookups for a quiz that does not exist."""
    return JSONResponse(
        status_code=404,
        content={"detail": QUIZ_NOT_FOUND_MESSAGE},
    )


@app.exception_handler(QuizAlreadyExistsException)
async def quiz_already_exists_handler(request: Request, exc: QuizAlreadyExistsException):
    """Handle attempts to create a duplicate quiz within a category."""
    return JSONResponse(
        status_code=400,
        content={"detail": QUIZ_ALREADY_EXISTS_MESSAGE},
    )


app.include_router(auth_router)
app.include_router(category_router)
app.include_router(quiz_router)


@app.get("/")
def health_check():
    """
    Check if the Assessment Portal API is running.
    """
    return {"message": "Assessment Portal API is running"}