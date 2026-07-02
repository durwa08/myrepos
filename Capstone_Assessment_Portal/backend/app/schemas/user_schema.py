import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.constants import INVALID_PASSWORD_MESSAGE

PASSWORD_PATTERN = re.compile(
    r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
)


class UserRegisterRequest(BaseModel):
    """Request model for user registration."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """
        Ensure the password has at least 8 characters, one uppercase
        letter, one digit, and one special character.
        """
        if not PASSWORD_PATTERN.match(value):
            raise ValueError(INVALID_PASSWORD_MESSAGE)
        return value


class UserResponse(BaseModel):
    """Response model containing public user information."""

    id: str
    username: str
    email: str
    role: str

    class Config:
        """Pydantic configuration for ORM attribute support."""

        from_attributes = True