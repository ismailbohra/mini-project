from typing import List, Optional

from app.auth.model import RoleType
from app.auth.repository import AuthRepository
from app.auth.service import AuthService
from app.config.database import get_session
from app.config.security import decode_token
from app.utils.exceptions import ForbiddenException, UnauthorizedException
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
) -> str:
    """Extract user role from JWT token."""
    token = credentials.credentials

    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    role = payload.get("role")
    if not role:
        raise UnauthorizedException("Invalid token payload - missing role")
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
