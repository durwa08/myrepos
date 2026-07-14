from fastapi import APIRouter, Depends, status
from app.schemas.user_schema import UserRegisterRequest, UserResponse
from app.schemas.auth_schema import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    RefreshResponse,
)
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import (
    get_current_user,
    require_admin,
)

# all auth related routes go here, mounted with /auth prefix in main.py
router = APIRouter(prefix="/auth", tags=["Authentication"])

# reusing the same service instance for every request
auth_service = AuthService()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(request: UserRegisterRequest):
    """
    Creates a new user, admin or student.
    Service takes care of checking duplicate emails (400 if found).
    """
    return await auth_service.register_user(request)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(request: LoginRequest):
    """
    Logs the user in and returns a JWT + role.
    """
    return await auth_service.login_user(request)


@router.get("/check-email")
async def check_email(email: str):
    """
    Checks whether an email is already registered.
    """
    return await auth_service.check_email(email)


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(request: RefreshRequest):
    """
    Client sends refresh token here when access token expires,
    gets a new access token back.
    """
    return await auth_service.refresh_access_token(request.refresh_token)


@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Temp route to check if the token is working.
    """
    return {
        "message": "You are authenticated!",
        "your_data": current_user,
    }


@router.get("/admin-only")
async def admin_only_test(current_user: dict = Depends(require_admin)):
    """
    Same idea but only admins should be able to hit this.
    """
    return {
        "message": "You are an admin, welcome!",
        "your_data": current_user,
    }