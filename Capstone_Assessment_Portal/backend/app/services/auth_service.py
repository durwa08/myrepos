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


class AuthService:
    """Service class for handling user authentication and authorization."""

    async def register_user(self, request: UserRegisterRequest) -> UserResponse:
        """
        Register a new user after validating that the email is unique.

        The password is hashed before storing. Every user registered
        through this endpoint is created with the student role — admin
        accounts are created separately via a standalone seed script.
        """
        existing_user = await get_user_by_email(request.email)
        if existing_user is not None:
            raise UserAlreadyExistsException()

        hashed = hash_password(request.password)

        new_user = UserModel(
            username=request.username,
            email=request.email,
            hashed_password=hashed,
            role=STUDENT_ROLE,
        )
        created_user = await create_user(new_user)

        return UserResponse(**serialize_user(created_user))

    async def login_user(self, request: LoginRequest) -> TokenResponse:
        """
        Authenticate a user and return access and refresh tokens.

        Returns the same error message for invalid email and password
        to avoid revealing whether an email is registered.
        """
        user = await get_user_by_email(request.email)
        if user is None:
            raise InvalidCredentialsException()

        if not verify_password(request.password, user["hashed_password"]):
            raise InvalidCredentialsException()

        token_data = {"sub": user["email"], "role": user["role"]}
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
        Validate the refresh token and issue a new access token.

        Verifies that the user still exists before generating
        a new access token.
        """
        payload = decode_refresh_token(refresh_token)

        user = await get_user_by_email(payload["sub"])
        if user is None:
            raise UserNotFoundException()

        new_access_token = create_access_token(
            data={"sub": user["email"], "role": user["role"]}
        )

        return RefreshResponse(
            access_token=new_access_token,
            token_type="bearer",
        )