"""
Test cases for password hashing and JWT token utilities.
"""

import pytest

from app.exceptions.custom_exceptions import InvalidTokenException
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    """
    Test that a password can be hashed and verified successfully.
    """
    password = "Password@123"
    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)


def test_verify_password_fails_for_wrong_password():
    """
    Test that verification fails for an incorrect password.
    """
    hashed_password = hash_password("Password@123")
    assert not verify_password("WrongPassword@123", hashed_password)


def test_create_and_decode_access_token():
    """
    Test that an access token can be created and decoded correctly.
    """
    token_data = {"sub": "durwa08@gmail.com", "role": "student"}
    token = create_access_token(token_data)

    payload = decode_access_token(token)

    assert payload["sub"] == "durwa08@gmail.com"
    assert payload["role"] == "student"
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token():
    """
    Test that a refresh token can be created and decoded correctly.
    """
    token_data = {"sub": "durwa08@gmail.com", "role": "student"}
    token = create_refresh_token(token_data)

    payload = decode_refresh_token(token)

    assert payload["type"] == "refresh"


def test_decode_access_token_rejects_invalid_token():
    """
    Test that decoding a malformed token raises InvalidTokenException.
    """
    with pytest.raises(InvalidTokenException):
        decode_access_token("not.a.valid.token")


def test_decode_access_token_rejects_refresh_token():
    """
    Test that a refresh token cannot be used as an access token.
    """
    token_data = {"sub": "durwa08@gmail.com", "role": "student"}
    refresh_token = create_refresh_token(token_data)

    with pytest.raises(InvalidTokenException):
        decode_access_token(refresh_token)


def test_decode_refresh_token_rejects_access_token():
    """
    Test that an access token cannot be used as a refresh token.
    """
    token_data = {"sub": "durwa08@gmail.com", "role": "student"}
    access_token = create_access_token(token_data)

    with pytest.raises(InvalidTokenException):
        decode_refresh_token(access_token)