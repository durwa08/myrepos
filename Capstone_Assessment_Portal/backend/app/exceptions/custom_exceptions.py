from fastapi import HTTPException, status


class InvalidTokenException(HTTPException):
    def __init__(self, detail: str = "Invalid or expired token."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AdminPrivilegeRequiredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires admin privileges.",
        )

class UserAlreadyExistsException(Exception):
    """Raised when a user with the given email already exists."""
    pass


class InvalidCredentialsException(Exception):
    """Raised when the provided login credentials are invalid."""
    pass


class InvalidRefreshTokenException(Exception):
    """Raised when the refresh token is invalid or expired."""
    pass


class UserNotFoundException(Exception):
    """Raised when the user no longer exists."""
    pass

class InvalidTokenException(Exception):
    """Raised when the JWT token is invalid or expired."""

class CategoryAlreadyExistsException(Exception):
    """Raised when a category with the given name already exists."""
    pass


class CategoryNotFoundException(Exception):
    """Raised when the requested category does not exist."""
    pass    

class QuestionNotFoundException(Exception):
    """Raised when a question with the given id does not exist."""


class QuestionAlreadyExistsException(Exception):
    """Raised when a question with the same text already exists within the quiz."""