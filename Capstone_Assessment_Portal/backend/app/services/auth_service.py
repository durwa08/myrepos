import base64
import binascii

from app.constants import STUDENT_ROLE
from app.repositories.user_repository import (
    get_user_by_email,
    create_user,
    serialize_user,
)
from app.models.user_model import UserModel
from app.schemas.user_schema import UserRegisterRequest, UserResponse
from app.schemas.auth_schema import (
    LoginRequest,
    TokenResponse,
    RefreshResponse,
)
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.exceptions.custom_exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    InvalidRefreshTokenException,
    UserNotFoundException,
)


def _decode_password(encoded_password: str) -> str:
    """
    Decode a Base64-encoded password received from the frontend back
    into its original plaintext form.

    The frontend Base64-encodes the password before sending it (see
    authService.js). This is encoding, not encryption or hashing - it
    provides no security benefit on its own and is fully reversible.
    Real protection against interception comes from HTTPS; this step
    only undoes the frontend's encoding so hashing/verification below
    operates on the real password, exactly as before this change.

    Raises InvalidCredentialsException if the value isn't valid
    Base64, so a malformed/tampered request fails the same way bad
    credentials would rather than raising an unhandled error.
    """
    try:
        decoded_bytes = base64.b64decode(encoded_password, validate=True)
        return decoded_bytes.decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError) as exc:
        raise InvalidCredentialsException() from exc


class AuthService:
    """Service class for handling user authentication and authorization."""

    async def register_user(self, request: UserRegisterRequest) -> UserResponse:
        """
        Register a new user after validating that the email is unique.
        """
        existing_user = await get_user_by_email(request.email)

        if existing_user is not None:
            raise UserAlreadyExistsException()

        plain_password = _decode_password(request.password)
        hashed = hash_password(plain_password)

        new_user = UserModel(
            username=request.username,
            email=request.email,
            hashed_password=hashed,
            role=STUDENT_ROLE,
        )

        created_user = await create_user(new_user)

        return UserResponse(**serialize_user(created_user))


    async def check_email(self, email: str) -> dict:
        """
        Check whether an email is already registered.
        """
        user = await get_user_by_email(email)

        return {
            "exists": user is not None
        }


    async def login_user(self, request: LoginRequest) -> TokenResponse:
        """
        Authenticate a user and return access and refresh tokens.
        """
        user = await get_user_by_email(request.email)

        if user is None:
            raise InvalidCredentialsException()

        plain_password = _decode_password(request.password)

        if not verify_password(plain_password, user["hashed_password"]):
            raise InvalidCredentialsException()

        token_data = {
            "sub": user["email"],
            "role": user["role"]
        }

        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            role=user["role"],
        )


    async def refresh_access_token(self, refresh_token: str) -> RefreshResponse:
        """
        Validate refresh token and generate a new access token.
        """
        payload = decode_refresh_token(refresh_token)

        user = await get_user_by_email(payload["sub"])

        if user is None:
            raise UserNotFoundException()

        new_access_token = create_access_token(
            data={
                "sub": user["email"],
                "role": user["role"]
            }
        )

        return RefreshResponse(
            access_token=new_access_token,
            token_type="bearer",
        )