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


class CategoryNotFoundException(Exception):
    """Raised when a category with the given id does not exist."""


class CategoryAlreadyExistsException(Exception):
    """Raised when a category with the given name already exists."""


class QuizNotFoundException(Exception):
    """Raised when a quiz with the given id does not exist."""


class QuizAlreadyExistsException(Exception):
    """Raised when a quiz with the same title already exists within the category."""


class QuestionNotFoundException(Exception):
    """Raised when a question with the given id does not exist."""


class QuestionAlreadyExistsException(Exception):
    """Raised when a question with the same text already exists within the quiz."""


class AttemptNotFoundException(Exception):
    """Raised when an attempt with the given id does not exist."""


class MaxAttemptsReachedException(Exception):
    """Raised when a student has already used all allowed attempts for a quiz."""


class StudentPrivilegeRequiredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires student privileges.",
        )


class AttemptExpiredException(Exception):
    """Raised when an attempt is accessed or modified after its time limit has passed."""


class AttemptAccessDeniedException(Exception):
    """Raised when a student tries to access an attempt that isn't theirs."""


class InvalidAttemptAnswerException(Exception):
    """Raised when a submitted answer references a question or option
    index that doesn't belong to the current attempt."""

    def __init__(self, detail: str = "Invalid answer for this attempt."):
        self.detail = detail
        super().__init__(detail)