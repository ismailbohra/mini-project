"""Middleware to verify user role hasn't been modified."""

from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.repository import AuthRepository
from app.config.database import get_session
from app.config.security import decode_token
from app.utils.exceptions import UnauthorizedException
from app.utils.logging import get_logger
from app.utils.redis import get_user_role_from_cache, set_user_role_in_cache

logger = get_logger(__name__)


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
