"""
Test cases for user request/response schemas.
"""

import pytest
from pydantic import ValidationError

from app.schemas.user_schema import UserRegisterRequest, UserResponse



def test_user_register_invalid_email():
    """
    Test registration fails when the email is not a valid format.
    """
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            username="durwa08",
            email="not-an-email",
            password="Password@123",
        )


def test_user_register_username_too_short():
    """
    Test registration fails when username is below the minimum length.
    """
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            username="na",
            email="durwa08@gmail.com",
            password="Password@123",
        )


def test_user_register_password_missing_uppercase():
    """
    Test registration fails when password has no uppercase letter.
    """
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            username="durwa08",
            email="durwa08@gmail.com",
            password="password@123",
        )


def test_user_register_password_missing_digit():
    """
    Test registration fails when password has no digit.
    """
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            username="durwa08",
            email="durwa08@gmail.com",
            password="Password@abc",
        )


def test_user_register_password_missing_special_char():
    """
    Test registration fails when password has no special character.
    """
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            username="durwa08",
            email="durwa08@gmail.com",
            password="Password123",
        )


def test_user_register_password_too_short():
    """
    Test registration fails when password is below 8 characters.
    """
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            username="durwa08",
            email="durwa08@gmail.com",
            password="Pass@1",
        )




def test_user_response_schema():
    """
    Test the response schema holds the expected public fields.
    """
    user_response = UserResponse(
        id="1",
        username="durwa08",
        email="durwa08@gmail.com",
        role="student",
    )
    assert user_response.role == "student"
    assert user_response.email == "durwa08@gmail.com"