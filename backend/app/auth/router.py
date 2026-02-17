from app.auth.dependency import get_auth_service, get_current_user_id
from app.auth.schema import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
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


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Forgot password",
    description="Request a password reset link to be sent via email",
)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Request password reset:
    - **email**: User's email address

    A password reset link will be sent to the email if it exists in the system.
    For security reasons, the response will be the same whether the email exists or not.
    """
    result = await auth_service.forgot_password(request)
    return MessageResponse(**result)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password",
    description="Reset password using the token received via email",
)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Reset password with token:
    - **token**: Password reset token from email
    - **new_password**: New password (minimum 8 characters)

    Requires valid reset token that hasn't expired.
    """
    result = await auth_service.reset_password(request)
    return MessageResponse(**result)
