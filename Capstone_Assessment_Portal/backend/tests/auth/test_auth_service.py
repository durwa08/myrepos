"""
Test cases for AuthService.
"""

from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.schemas.auth_schema import LoginRequest, RefreshRequest
from app.schemas.user_schema import UserRegisterRequest
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_user_success(mocker):
    """
    Test successful registration when the email is not already taken.
    """
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        new_callable=AsyncMock,
        return_value=None,
    )
    mocker.patch(
        "app.services.auth_service.create_user",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "username": "durwa08",
            "email": "durwa08@gmail.com",
            "hashed_password": "hashed_password",
            "role": "student",
        },
    )
    mocker.patch(
        "app.services.auth_service.hash_password",
        return_value="hashed_password",
    )

    service = AuthService()
    request = UserRegisterRequest(
        username="durwa08",
        email="durwa08@gmail.com",
        password="Password@123",
    )

    response = await service.register_user(request)

    assert response.email == "durwa08@gmail.com"
    assert response.role == "student"


@pytest.mark.asyncio
async def test_register_user_duplicate_email(mocker):
    """
    Test registration fails when the email is already registered.
    """
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        new_callable=AsyncMock,
        return_value={"email": "durwa08@gmail.com"},
    )

    service = AuthService()
    request = UserRegisterRequest(
        username="durwa08",
        email="durwa08@gmail.com",
        password="Password@123",
    )

    with pytest.raises(UserAlreadyExistsException):
        await service.register_user(request)


@pytest.mark.asyncio
async def test_login_user_success(mocker):
    """
    Test successful login returns access and refresh tokens.
    """
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        new_callable=AsyncMock,
        return_value={
            "email": "durwa08@gmail.com",
            "hashed_password": "hashed_password",
            "role": "student",
        },
    )
    mocker.patch(
        "app.services.auth_service.verify_password",
        return_value=True,
    )
    mocker.patch(
        "app.services.auth_service.create_access_token",
        return_value="access_token",
    )
    mocker.patch(
        "app.services.auth_service.create_refresh_token",
        return_value="refresh_token",
    )

    service = AuthService()
    request = LoginRequest(email="durwa08@gmail.com", password="Password@123")

    response = await service.login_user(request)

    assert response.access_token == "access_token"
    assert response.refresh_token == "refresh_token"
    assert response.role == "student"


@pytest.mark.asyncio
async def test_login_user_not_found(mocker):
    """
    Test login fails when no user matches the given email.
    """
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = AuthService()
    request = LoginRequest(email="missing@gmail.com", password="Password@123")

    with pytest.raises(InvalidCredentialsException):
        await service.login_user(request)


@pytest.mark.asyncio
async def test_login_user_wrong_password(mocker):
    """
    Test login fails when the password does not match.
    """
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        new_callable=AsyncMock,
        return_value={
            "email": "durwa08@gmail.com",
            "hashed_password": "hashed_password",
            "role": "student",
        },
    )
    mocker.patch(
        "app.services.auth_service.verify_password",
        return_value=False,
    )

    service = AuthService()
    request = LoginRequest(email="durwa08@gmail.com", password="WrongPassword@123")

    with pytest.raises(InvalidCredentialsException):
        await service.login_user(request)


@pytest.mark.asyncio
async def test_refresh_access_token_success(mocker):
    """
    Test that a valid refresh token produces a new access token.
    """
    mocker.patch(
        "app.services.auth_service.decode_refresh_token",
        return_value={"sub": "durwa08@gmail.com", "role": "student"},
    )
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        new_callable=AsyncMock,
        return_value={"email": "durwa08@gmail.com", "role": "student"},
    )
    mocker.patch(
        "app.services.auth_service.create_access_token",
        return_value="new_access_token",
    )

    service = AuthService()
    response = await service.refresh_access_token("refresh_token")

    assert response.access_token == "new_access_token"


@pytest.mark.asyncio
async def test_refresh_access_token_user_not_found(mocker):
    """
    Test refresh fails when the user no longer exists.
    """
    mocker.patch(
        "app.services.auth_service.decode_refresh_token",
        return_value={"sub": "missing@gmail.com", "role": "student"},
    )
    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = AuthService()
    with pytest.raises(UserNotFoundException):
        await service.refresh_access_token("refresh_token")


@pytest.mark.asyncio
async def test_refresh_access_token_invalid_token(mocker):
    """
    Test refresh fails when the refresh token itself is invalid.
    """
    mocker.patch(
        "app.services.auth_service.decode_refresh_token",
        side_effect=InvalidTokenException("Invalid refresh token."),
    )

    service = AuthService()
    with pytest.raises(InvalidTokenException):
        await service.refresh_access_token("bad_token")