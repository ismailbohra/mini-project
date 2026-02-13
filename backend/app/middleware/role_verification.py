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

    If the role has been modified (e.g., by an admin), the user will be forced to re-login
    to get a new token with the updated role.

    This middleware:
    1. Extracts the JWT token from the Authorization header
    2. Decodes the token and retrieves the role claim
    3. Fetches the current role from the database/cache
    4. Compares both roles and rejects the request if they don't match
    """

    # Paths that don't require role verification
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
        """Process the request and verify role if token is present."""

        # Skip role verification for excluded paths
        if any(request.url.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return await call_next(request)

        # Check if Authorization header is present
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # No token, let the endpoint handle authentication
            return await call_next(request)

        try:
            # Extract token
            token = auth_header.split(" ")[1]

            # Decode token
            payload = decode_token(token)
            if not payload:
                # Invalid token, let the endpoint handle it
                return await call_next(request)

            # Get user ID and role from token
            user_id = payload.get("sub")
            token_role = payload.get("role")

            if not user_id or not token_role:
                # Token doesn't have required fields, let endpoint handle it
                return await call_next(request)

            try:
                user_id_int = int(user_id)
            except ValueError:
                return await call_next(request)

            # Get current role from cache/database
            current_role = await self._get_current_user_role(request, user_id_int)

            # Compare roles
            if current_role and token_role != current_role:
                logger.warning(
                    f"Role mismatch detected for user {user_id_int}. "
                    f"Token role: {token_role}, Current role: {current_role}"
                )
                response = JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "success": False,
                        "error": {
                            "code": "ROLE_MODIFIED",
                            "message": "Your role has been modified. Please login again to continue.",
                        },
                        "detail": "Your role has been modified. Please login again to continue.",
                    },
                )
                # Add CORS headers manually since we're bypassing normal response flow
                response.headers["Access-Control-Allow-Origin"] = "*"
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "*"
                response.headers["Access-Control-Allow-Headers"] = "*"
                return response

            # Role matches or couldn't be verified, proceed with request
            return await call_next(request)

        except UnauthorizedException as e:
            # Convert exception to JSON response instead of re-raising
            logger.error(
                f"Authentication error in middleware: {e.message if hasattr(e, 'message') else str(e)}"
            )
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": str(e.message) if hasattr(e, "message") else str(e),
                    },
                    "detail": str(e.message) if hasattr(e, "message") else str(e),
                },
            )
            # Add CORS headers manually
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
            return response
        except Exception as e:
            # Log unexpected errors but don't block the request
            logger.error(f"Error in role verification middleware: {e}")
            return await call_next(request)

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
