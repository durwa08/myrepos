"""
Test cases for authentication middleware (dependency functions).
"""

from unittest.mock import MagicMock

import pytest

from app.exceptions.custom_exceptions import (
    AdminPrivilegeRequiredException,
    InvalidTokenException,
)
from app.middleware.auth_middleware import get_current_user, require_admin


@pytest.mark.asyncio
async def test_get_current_user_valid_token(mocker):
    """
    Test that a valid token returns the decoded payload.
    """
    mocker.patch(
        "app.middleware.auth_middleware.decode_access_token",
        return_value={"sub": "durwa08@gmail.com", "role": "student"},
    )

    credentials = MagicMock()
    credentials.credentials = "valid_token"

    result = await get_current_user(credentials)

    assert result["sub"] == "durwa08@gmail.com"
    assert result["role"] == "student"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mocker):
    """
    Test that a token decoding to None raises InvalidTokenException.
    """
    mocker.patch(
        "app.middleware.auth_middleware.decode_access_token",
        return_value=None,
    )

    credentials = MagicMock()
    credentials.credentials = "bad_token"

    with pytest.raises(InvalidTokenException):
        await get_current_user(credentials)


@pytest.mark.asyncio
async def test_require_admin_success():
    """
    Test that an admin user passes the admin check.
    """
    admin_user = {"sub": "durwapahariya08@gmail.com", "role": "admin"}

    result = await require_admin(admin_user)

    assert result == admin_user


@pytest.mark.asyncio
async def test_require_admin_forbidden_for_student():
    """
    Test that a non-admin user is rejected with a 403-style exception.
    """
    student_user = {"sub": "durwa08@gmail.com", "role": "student"}

    with pytest.raises(AdminPrivilegeRequiredException):
        await require_admin(student_user)