"""Middleware to verify user role hasn't been modified."""

from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.repository import AuthRepository
from app.config.database import get_session
from app.utils.exceptions import UnauthorizedException
from app.utils.logging import get_logger
from app.utils.redis import delete_cache, get_cache, set_cache
from app.utils.security import decode_token

logger = get_logger(__name__)

# Role cache configuration
ROLE_CACHE_KEY_PREFIX = "user_role:"
ROLE_CACHE_EXPIRY = 3600  # 1 hour


def get_role_cache_key(user_id: int) -> str:
    """Generate Redis key for user role cache."""
    return f"{ROLE_CACHE_KEY_PREFIX}{user_id}"


async def get_user_role_from_cache(user_id: int) -> Optional[str]:
    """Get user role from Redis cache."""
    key = get_role_cache_key(user_id)
    return await get_cache(key)


async def set_user_role_in_cache(user_id: int, role: str) -> bool:
    """Set user role in Redis cache with expiry."""
    key = get_role_cache_key(user_id)
    return await set_cache(key, role, expire=ROLE_CACHE_EXPIRY)


async def clear_user_role_cache(user_id: int) -> bool:
    """Clear user role from Redis cache."""
    key = get_role_cache_key(user_id)
    return await delete_cache(key)


class RoleVerificationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify that a user's role in their JWT token matches their current role in the database.
    """

    EXCLUDED_PATHS = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/auth/login",
        "/api/auth/register",
        "/assets",
    ]

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:

        # Skip role verification for excluded paths
        if any(request.url.path.startswith(path) for path in self.EXCLUDED_PATHS):
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response

        try:
            token = auth_header.split(" ")[1]
            payload = decode_token(token)

            if not payload:
                response = await call_next(request)
                response.headers["Access-Control-Allow-Origin"] = "*"
                return response

            user_id = payload.get("sub")
            token_role = payload.get("role")

            if not user_id or not token_role:
                response = await call_next(request)
                response.headers["Access-Control-Allow-Origin"] = "*"
                return response

            try:
                user_id_int = int(user_id)
            except ValueError:
                response = await call_next(request)
                response.headers["Access-Control-Allow-Origin"] = "*"
                return response

            current_role = await self._get_current_user_role(request, user_id_int)

            if current_role and token_role != current_role:
                logger.warning(
                    f"Role mismatch detected for user {user_id_int}. "
                    f"Token role: {token_role}, Current role: {current_role}"
                )
                # Return a structured JSON error matching the app's standard
                payload = {
                    "success": False,
                    "error": {
                        "code": "ROLE_MODIFIED",
                        "message": "Your role has been modified. Please login again to continue.",
                    },
                    "data": None,
                }
                resp = JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED, content=payload
                )
                # Ensure CORS headers are present so browser can read the response
                resp.headers["Access-Control-Allow-Origin"] = "*"
                resp.headers["Access-Control-Allow-Credentials"] = "true"
                resp.headers["Access-Control-Allow-Methods"] = (
                    "GET,POST,PUT,DELETE,OPTIONS"
                )
                resp.headers["Access-Control-Allow-Headers"] = (
                    "Authorization,Content-Type"
                )
                return resp

            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response

        except UnauthorizedException as exc:
            # Convert exception to the application's JSON error shape
            message = getattr(exc, "message", str(exc))
            payload = {
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": message,
                },
                "data": None,
            }
            resp = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, content=payload
            )
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Credentials"] = "true"
            resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type"
            return resp

        except Exception as e:
            logger.error(f"Error in role verification middleware: {e}")
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response

    async def _get_current_user_role(
        self, request: Request, user_id: int
    ) -> str | None:
        """
        Get the current role for a user from cache or database.

        Args:
            request: The FastAPI request object
            user_id: The user ID to look up

        Returns:
            The current role string or None if user not found
        """
        try:
            # Try to get role from Redis cache first
            cached_role = await get_user_role_from_cache(user_id)
            if cached_role:
                return cached_role

            # If not in cache, fetch from database
            async for session in get_session():
                repository = AuthRepository(session)
                user = await repository.get_user_by_id(user_id)

                if user and user.is_active and not user.is_deleted:
                    role = user.role.value
                    # Cache the role for future requests
                    await set_user_role_in_cache(user_id, role)
                    return role

                return None

        except Exception as e:
            logger.error(f"Error fetching user role for user {user_id}: {e}")
            return None
