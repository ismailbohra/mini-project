from typing import List, Optional

from app.auth.repository import AuthRepository
from app.auth.service import AuthService
from app.config.database import get_session
from app.config.security import decode_token
from app.users.model import RoleType
from app.utils.exceptions import ForbiddenException, UnauthorizedException
from app.utils.redis import (
    get_user_role_from_cache,
    set_user_role_in_cache,
)
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    """Get auth service dependency."""
    repository = AuthRepository(session)
    return AuthService(repository)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """Extract and validate user ID from JWT token."""
    token = credentials.credentials

    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    try:
        return int(user_id)
    except ValueError:
        raise UnauthorizedException("Invalid user ID in token")


async def get_current_user_id_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
) -> Optional[int]:
    """Extract user ID from JWT token if provided, otherwise return None."""
    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        return int(user_id)
    except ValueError:
        return None


async def get_current_user_role(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> str:
    """
    Extract and validate user role with Redis caching.

    Flow:
    1. Validate token and extract user ID
    2. Check Redis cache for user role
    3. If not in cache, fetch from database and update cache
    4. Return the role for authorization
    """
    token = credentials.credentials

    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise UnauthorizedException("Invalid user ID in token")

    # Try to get role from Redis cache
    cached_role = await get_user_role_from_cache(user_id_int)
    if cached_role:
        return cached_role

    # If not in cache, fetch from database
    repository = AuthRepository(session)
    user = await repository.get_user_by_id(user_id_int)

    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active or user.is_deleted:
        status_msg = "inactive" if not user.is_active else "deleted"
        raise UnauthorizedException(f"User account is {status_msg}")

    # Store role in Redis cache for future requests
    role = user.role.value
    await set_user_role_in_cache(user_id_int, role)

    return role


class RoleChecker:
    """Dependency to check if user has required role."""

    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles

    async def __call__(self, user_role: str = Depends(get_current_user_role)):
        """Check if user has one of the required roles."""
        if user_role not in self.required_roles:
            raise ForbiddenException(
                f"Access denied. Required roles: {', '.join(self.required_roles)}"
            )
        return True


# Pre-configured role checkers
require_admin = RoleChecker([RoleType.ADMIN.value])
require_moderator = RoleChecker([RoleType.ADMIN.value, RoleType.MODERATOR.value])
require_user = RoleChecker(
    [RoleType.ADMIN.value, RoleType.MODERATOR.value, RoleType.USER.value]
)
