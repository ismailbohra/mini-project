from datetime import timedelta
from typing import Any, Dict

from app.auth.repository import AuthRepository
from app.auth.schema import (
    ChangePasswordRequest,
    TokenResponse,
    UserLoginRequest,
    UserResponse,
)
from app.users.model import User
from app.utils.exceptions import (
    InvalidPasswordException,
    NotFoundException,
    UnauthorizedException,
)
from app.utils.logging import get_logger
from app.utils.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    validate_password,
    verify_password,
)

logger = get_logger(__name__)


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def login(self, request: UserLoginRequest) -> TokenResponse:
        """Login user and return JWT token."""
        try:
            # Get user by username
            user = await self.repository.get_user_by_email(request.email)

            if not user:
                raise UnauthorizedException("Invalid username or password")

            # Verify password
            if not verify_password(request.password, user.hashed_password):
                raise UnauthorizedException("Invalid username or password")

            # Check if user is active
            if not user.is_active:
                raise UnauthorizedException("User account is inactive")

            # Update role cache on login to ensure it's fresh
            from app.middleware.role_verification import set_user_role_in_cache

            await set_user_role_in_cache(user.id, user.role.value)

            # Generate access token
            token_data = self._create_token_data(user)
            access_token = create_access_token(
                data=token_data,
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            )

            logger.info(f"User {user.email} logged in successfully")
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=self._user_to_response(user),
            )
        except UnauthorizedException:
            logger.warning(f"Failed login attempt for email: {request.email}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during login for {request.email}: {e}")
            raise

    async def change_password(
        self, user_id: int, request: ChangePasswordRequest
    ) -> Dict[str, str]:
        """Change user password."""
        try:
            user = await self.repository.get_user_by_id(user_id)

            if not user:
                raise NotFoundException("User not found")

            # Verify old password
            if not verify_password(request.old_password, user.hashed_password):
                raise UnauthorizedException("Invalid old password")

            validate_password(request.new_password)

            # Hash new password
            new_hashed_password = get_password_hash(request.new_password)

            # Update password
            await self.repository.update_user_password(user, new_hashed_password)

            logger.info(f"Password changed successfully for user {user_id}")
            return {"message": "Password changed successfully"}
        except (NotFoundException, UnauthorizedException, InvalidPasswordException):
            raise
        except Exception as e:
            logger.exception(f"Error changing password for user {user_id}: {e}")
            raise

    async def get_current_user(self, user_id: int) -> UserResponse:
        """Get current user information."""
        user = await self.repository.get_user_by_id(user_id)

        if not user:
            raise NotFoundException("User not found")

        return self._user_to_response(user)

    def _create_token_data(self, user: User) -> Dict[str, Any]:
        """Create token payload with user data and role."""
        return {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
        }

    def _user_to_response(self, user: User) -> UserResponse:
        """Convert User model to UserResponse."""
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            role=user.role.value,
        )
