import pytest

from app.exceptions.custom_exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_user_success(mocker):
    """Test successful registration of a new user."""
    service = AuthService()

    request = mocker.Mock()
    request.username = "Durwa"
    request.email = "durwa@test.com"
    request.password = "cGFzc3dvcmQ="

    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value=None,
    )

    mocker.patch(
        "app.services.auth_service.hash_password",
        return_value="hashed_password",
    )

    created_user = {
        "_id": "507f1f77bcf86cd799439011",
        "username": "Durwa",
        "email": "durwa@test.com",
        "hashed_password": "hashed_password",
        "role": "student",
    }

    mocker.patch(
        "app.services.auth_service.create_user",
        return_value=created_user,
    )

    mocker.patch(
        "app.services.auth_service.serialize_user",
        return_value={
            "id": "507f1f77bcf86cd799439011",
            "username": "Durwa",
            "email": "durwa@test.com",
            "role": "student",
        },
    )

    response = await service.register_user(request)

    assert response.username == "Durwa"
    assert response.email == "durwa@test.com"


@pytest.mark.asyncio
async def test_register_existing_user(mocker):
    """Test registration when the email already exists."""
    service = AuthService()

    request = mocker.Mock()
    request.email = "durwa@test.com"

    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value={"email": "durwa@test.com"},
    )

    with pytest.raises(UserAlreadyExistsException):
        await service.register_user(request)


@pytest.mark.asyncio
async def test_check_email_exists(mocker):
    """Test checking an email that is already registered."""
    service = AuthService()

    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value={"email": "durwa@test.com"},
    )

    response = await service.check_email("durwa@test.com")

    assert response == {"exists": True}


@pytest.mark.asyncio
async def test_check_email_not_exists(mocker):
    """Test checking an email that is not registered."""
    service = AuthService()

    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value=None,
    )

    response = await service.check_email("durwa@test.com")

    assert response == {"exists": False}


@pytest.mark.asyncio
async def test_login_user_success(mocker):
    """Test successful login with valid credentials."""
    service = AuthService()

    request = mocker.Mock()
    request.email = "durwa@test.com"
    request.password = "cGFzc3dvcmQ="

    user = {
        "email": "durwa@test.com",
        "hashed_password": "hashed_password",
        "role": "student",
    }

    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value=user,
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

    response = await service.login_user(request)

    assert response.access_token == "access_token"
    assert response.refresh_token == "refresh_token"
    assert response.role == "student"
    assert response.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_user_not_found(mocker):
    """Test login when the user does not exist."""
    service = AuthService()

    request = mocker.Mock()
    request.email = "durwa@test.com"
    request.password = "cGFzc3dvcmQ="

    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value=None,
    )

    with pytest.raises(InvalidCredentialsException):
        await service.login_user(request)


@pytest.mark.asyncio
async def test_login_invalid_password(mocker):
    """Test login with an incorrect password."""
    service = AuthService()

    request = mocker.Mock()
    request.email = "durwa@test.com"
    request.password = "cGFzc3dvcmQ="

    user = {
        "email": "durwa@test.com",
        "hashed_password": "hashed_password",
        "role": "student",
    }

    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value=user,
    )

    mocker.patch(
        "app.services.auth_service.verify_password",
        return_value=False,
    )

    with pytest.raises(InvalidCredentialsException):
        await service.login_user(request)


@pytest.mark.asyncio
async def test_refresh_access_token_success(mocker):
    """Test generating a new access token using a valid refresh token."""
    service = AuthService()

    mocker.patch(
        "app.services.auth_service.decode_refresh_token",
        return_value={"sub": "durwa@test.com"},
    )

    user = {
        "email": "durwa@test.com",
        "role": "student",
    }

    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value=user,
    )

    mocker.patch(
        "app.services.auth_service.create_access_token",
        return_value="new_access_token",
    )

    response = await service.refresh_access_token("refresh_token")

    assert response.access_token == "new_access_token"
    assert response.token_type == "bearer"


@pytest.mark.asyncio
async def test_refresh_access_token_user_not_found(mocker):
    """Test refreshing an access token when the user no longer exists."""
    service = AuthService()

    mocker.patch(
        "app.services.auth_service.decode_refresh_token",
        return_value={"sub": "durwa@test.com"},
    )

    mocker.patch(
        "app.services.auth_service.get_user_by_email",
        return_value=None,
    )

    with pytest.raises(UserNotFoundException):
        await service.refresh_access_token("refresh_token")