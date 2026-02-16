"""
Unit tests for the middleware module.

Tests:
- Role verification middleware
- Role cache management
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.middleware.role_verification import (
    RoleVerificationMiddleware,
    clear_user_role_cache,
    get_role_cache_key,
    get_user_role_from_cache,
    set_user_role_in_cache,
)
from fastapi import Request, Response
from starlette.datastructures import Headers


@pytest.fixture
def mock_request():
    """Create a mock request."""
    request = MagicMock(spec=Request)
    request.url = MagicMock()
    request.headers = {}
    return request


@pytest.fixture
def mock_call_next():
    """Create a mock call_next function."""

    async def _call_next(request):
        response = MagicMock(spec=Response)
        response.headers = {}
        return response

    return _call_next


@pytest.mark.unit
@pytest.mark.asyncio
class TestRoleVerificationMiddleware:
    """Test cases for RoleVerificationMiddleware."""

    async def test_excluded_paths_skip_verification(self, mock_request, mock_call_next):
        """Test that excluded paths skip role verification."""
        mock_request.url.path = "/docs"

        middleware = RoleVerificationMiddleware(app=MagicMock())

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response is not None
        assert response.headers.get("Access-Control-Allow-Origin") == "*"

    async def test_login_path_skip_verification(self, mock_request, mock_call_next):
        """Test that login path skips verification."""
        mock_request.url.path = "/api/auth/login"

        middleware = RoleVerificationMiddleware(app=MagicMock())

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response is not None

    async def test_register_path_skip_verification(self, mock_request, mock_call_next):
        """Test that register path skips verification."""
        mock_request.url.path = "/api/auth/register"

        middleware = RoleVerificationMiddleware(app=MagicMock())

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response is not None

    async def test_assets_path_skip_verification(self, mock_request, mock_call_next):
        """Test that assets path skips verification."""
        mock_request.url.path = "/assets/image.jpg"

        middleware = RoleVerificationMiddleware(app=MagicMock())

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response is not None

    async def test_no_auth_header_skip_verification(self, mock_request, mock_call_next):
        """Test request without Authorization header."""
        mock_request.url.path = "/api/posts"
        mock_request.headers = {}

        middleware = RoleVerificationMiddleware(app=MagicMock())

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response is not None

    async def test_invalid_auth_header_skip_verification(
        self, mock_request, mock_call_next
    ):
        """Test request with invalid Authorization header."""
        mock_request.url.path = "/api/posts"
        mock_request.headers = MagicMock()
        mock_request.headers.get = MagicMock(return_value="InvalidToken")

        middleware = RoleVerificationMiddleware(app=MagicMock())

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response is not None

    async def test_valid_token_with_cached_role(self, mock_request, mock_call_next):
        """Test request with valid token and cached role."""
        mock_request.url.path = "/api/posts"
        mock_request.headers = MagicMock()
        mock_request.headers.get = MagicMock(return_value="Bearer valid_token")

        middleware = RoleVerificationMiddleware(app=MagicMock())

        with (
            patch("app.middleware.role_verification.decode_token") as mock_decode,
            patch(
                "app.middleware.role_verification.get_user_role_from_cache"
            ) as mock_get_cache,
        ):
            mock_decode.return_value = {"sub": "1", "role": "USER"}
            mock_get_cache.return_value = "USER"

            response = await middleware.dispatch(mock_request, mock_call_next)

            assert response is not None

    async def test_invalid_token_payload(self, mock_request, mock_call_next):
        """Test request with invalid token payload."""
        mock_request.url.path = "/api/posts"
        mock_request.headers = MagicMock()
        mock_request.headers.get = MagicMock(return_value="Bearer invalid_token")

        middleware = RoleVerificationMiddleware(app=MagicMock())

        with patch("app.middleware.role_verification.decode_token") as mock_decode:
            mock_decode.return_value = None

            response = await middleware.dispatch(mock_request, mock_call_next)

            assert response is not None

    async def test_token_missing_user_id(self, mock_request, mock_call_next):
        """Test token without user ID."""
        mock_request.url.path = "/api/posts"
        mock_request.headers = MagicMock()
        mock_request.headers.get = MagicMock(return_value="Bearer token")

        middleware = RoleVerificationMiddleware(app=MagicMock())

        with patch("app.middleware.role_verification.decode_token") as mock_decode:
            mock_decode.return_value = {"role": "USER"}

            response = await middleware.dispatch(mock_request, mock_call_next)

            assert response is not None

    async def test_token_missing_role(self, mock_request, mock_call_next):
        """Test token without role."""
        mock_request.url.path = "/api/posts"
        mock_request.headers = MagicMock()
        mock_request.headers.get = MagicMock(return_value="Bearer token")

        middleware = RoleVerificationMiddleware(app=MagicMock())

        with patch("app.middleware.role_verification.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": "1"}

            response = await middleware.dispatch(mock_request, mock_call_next)

            assert response is not None

    async def test_invalid_user_id_format(self, mock_request, mock_call_next):
        """Test token with invalid user ID format."""
        mock_request.url.path = "/api/posts"
        mock_request.headers = MagicMock()
        mock_request.headers.get = MagicMock(return_value="Bearer token")

        middleware = RoleVerificationMiddleware(app=MagicMock())

        with patch("app.middleware.role_verification.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": "invalid", "role": "USER"}

            response = await middleware.dispatch(mock_request, mock_call_next)

            assert response is not None


@pytest.mark.unit
class TestRoleCacheManagement:
    """Test cases for role cache management functions."""

    def test_get_role_cache_key(self):
        """Test generating role cache key."""
        key = get_role_cache_key(1)
        assert key == "user_role:1"

    def test_get_role_cache_key_different_users(self):
        """Test cache keys for different users."""
        key1 = get_role_cache_key(1)
        key2 = get_role_cache_key(2)
        assert key1 != key2

    @pytest.mark.asyncio
    async def test_get_user_role_from_cache(self):
        """Test retrieving user role from cache."""
        with patch("app.middleware.role_verification.get_cache") as mock_get:
            mock_get.return_value = "USER"

            role = await get_user_role_from_cache(1)

            assert role == "USER"
            mock_get.assert_called_once_with("user_role:1")

    @pytest.mark.asyncio
    async def test_get_user_role_from_cache_not_found(self):
        """Test retrieving role when not in cache."""
        with patch("app.middleware.role_verification.get_cache") as mock_get:
            mock_get.return_value = None

            role = await get_user_role_from_cache(1)

            assert role is None

    @pytest.mark.asyncio
    async def test_set_user_role_in_cache(self):
        """Test setting user role in cache."""
        with patch("app.middleware.role_verification.set_cache") as mock_set:
            mock_set.return_value = True

            result = await set_user_role_in_cache(1, "ADMIN")

            assert result is True
            mock_set.assert_called_once()
            args = mock_set.call_args
            assert args[0][0] == "user_role:1"
            assert args[0][1] == "ADMIN"

    @pytest.mark.asyncio
    async def test_clear_user_role_cache(self):
        """Test clearing user role from cache."""
        with patch("app.middleware.role_verification.delete_cache") as mock_delete:
            mock_delete.return_value = True

            result = await clear_user_role_cache(1)

            assert result is True
            mock_delete.assert_called_once_with("user_role:1")

    @pytest.mark.asyncio
    async def test_set_role_cache_failure(self):
        """Test handling cache set failure."""
        with patch("app.middleware.role_verification.set_cache") as mock_set:
            mock_set.return_value = False

            result = await set_user_role_in_cache(1, "USER")

            assert result is False

    @pytest.mark.asyncio
    async def test_clear_role_cache_failure(self):
        """Test handling cache clear failure."""
        with patch("app.middleware.role_verification.delete_cache") as mock_delete:
            mock_delete.return_value = False

            result = await clear_user_role_cache(1)

            assert result is False
