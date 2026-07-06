from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.exceptions.custom_exceptions import (
    InvalidTokenException,
    AdminPrivilegeRequiredException,
    StudentPrivilegeRequiredException,
)
from app.utils.security import decode_access_token

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Extract and validate the access token from the request.

    Returns the decoded token payload if the token is valid.
    Raises an exception if the token is invalid or expired.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise InvalidTokenException()

    return payload


async def require_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Verify that the authenticated user has the admin role.

    Raises an exception if the user is not an admin.
    """
    if current_user.get("role") != "admin":
        raise AdminPrivilegeRequiredException()

    return current_user


async def require_student(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Verify that the authenticated user has the student role.

    Raises an exception if the user is not a student.
    """
    if current_user.get("role") != "student":
        raise StudentPrivilegeRequiredException()

    return current_user
