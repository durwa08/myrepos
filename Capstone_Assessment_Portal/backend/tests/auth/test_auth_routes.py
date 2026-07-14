"""
Test cases for authentication routes.
"""

from unittest.mock import AsyncMock

from app.main import app
from app.middleware.auth_middleware import get_current_user, require_admin
from app.schemas.auth_schema import TokenResponse
from app.schemas.user_schema import UserResponse



def test_login_route(client, mocker):
    """
    Test the login endpoint returns 200 with tokens.
    """
    mocker.patch(
        "app.api.v1.auth_routes.AuthService.login_user",
        new=AsyncMock(
            return_value=TokenResponse(
                access_token="access_token",
                refresh_token="refresh_token",
                token_type="bearer",
                role="student",
            )
        ),
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "durwa08@gmail.com",
            "password": "Password@123",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "access_token"


def test_login_route_invalid_credentials(client, mocker):
    """
    Test the login endpoint returns 401 for invalid credentials.
    """
    from app.exceptions.custom_exceptions import InvalidCredentialsException

    mocker.patch(
        "app.api.v1.auth_routes.AuthService.login_user",
        new=AsyncMock(side_effect=InvalidCredentialsException()),
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "durwa08@gmail.com",
            "password": "WrongPassword@123",
        },
    )

    assert response.status_code == 401


def test_get_my_profile_route(client):
    """
    Test the /auth/me route returns the authenticated user's payload.
    """
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "durwa08@gmail.com",
        "role": "student",
    }

    response = client.get(
        "/auth/me", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()["your_data"]["sub"] == "durwa08@gmail.com"

    app.dependency_overrides.clear()


def test_get_my_profile_route_without_token(client):
    """
    Test the /auth/me route returns 403 without a token.
    """
    response = client.get("/auth/me")

    assert response.status_code in (401, 403)


def test_admin_only_route_as_admin(client):
    """
    Test the /auth/admin-only route succeeds for an admin user.
    """
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    response = client.get(
        "/auth/admin-only", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "You are an admin, welcome!"

    app.dependency_overrides.clear()