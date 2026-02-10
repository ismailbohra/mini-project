from app.auth.dependency import get_auth_service, get_current_user_id
from app.auth.schema import (
    ChangePasswordRequest,
    MessageResponse,
    TokenResponse,
    UserLoginRequest,
)
from app.auth.service import AuthService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user and return JWT token with user data and roles",
)
async def login(
    request: UserLoginRequest, auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Login with:
    - **username**: User's username
    - **password**: User's password

    Returns JWT token containing user information and assigned roles.
    """
    return await auth_service.login(request)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change the current user's password",
)
async def change_password(
    request: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Change password for the authenticated user:
    - **old_password**: Current password
    - **new_password**: New password (minimum 8 characters)

    Requires valid JWT token in Authorization header.
    """
    result = await auth_service.change_password(user_id, request)
    return MessageResponse(**result)
