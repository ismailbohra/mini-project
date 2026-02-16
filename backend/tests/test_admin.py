"""
Unit tests for the admin module.

Tests:
- Get all users
- Assign role to user
- Toggle user active status
- Get dashboard analytics
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.admin.schema import (
    AssignRoleRequest,
    DashboardAnalyticsResponse,
    ToggleUserResponse,
)
from app.admin.service import AdminService
from app.users.model import RoleType, User
from app.utils.exceptions import NotFoundException, UserNotFoundException
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_admin_repository():
    """Create a mock admin repository."""
    repository = AsyncMock()
    return repository


@pytest.fixture
def admin_service(mock_admin_repository):
    """Create an AdminService instance with mock repository."""
    return AdminService(mock_admin_repository)


@pytest.fixture
def test_user():
    """Create a test user."""
    from datetime import datetime

    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword",
        is_active=True,
        role=RoleType.USER,
    )
    user.created_at = datetime.now()
    user.updated_at = datetime.now()
    return user


@pytest.fixture
def admin_user():
    """Create an admin user."""
    from datetime import datetime

    user = User(
        id=2,
        username="adminuser",
        email="admin@example.com",
        hashed_password="hashedpassword",
        is_active=True,
        role=RoleType.ADMIN,
    )
    user.created_at = datetime.now()
    user.updated_at = datetime.now()
    return user


@pytest.mark.unit
@pytest.mark.asyncio
class TestAdminService:
    """Test cases for AdminService."""

    async def test_get_all_users_success(self, admin_service, test_user, admin_user):
        """Test getting all users successfully."""
        admin_service.repository.get_all_users.return_value = [test_user, admin_user]

        result = await admin_service.get_all_users(skip=0, limit=100)

        assert len(result) == 2
        assert result[0].username == "testuser"
        assert result[1].username == "adminuser"
        admin_service.repository.get_all_users.assert_called_once_with(0, 100)

    async def test_get_all_users_empty(self, admin_service):
        """Test getting all users when database is empty."""
        admin_service.repository.get_all_users.return_value = []

        result = await admin_service.get_all_users(skip=0, limit=100)

        assert len(result) == 0
        admin_service.repository.get_all_users.assert_called_once_with(0, 100)

    async def test_assign_role_success(self, admin_service, test_user):
        """Test assigning a role to user successfully."""
        from datetime import datetime

        request = AssignRoleRequest(user_id=1, role="Moderator")
        admin_service.repository.get_user_by_id.return_value = test_user

        updated_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            is_active=True,
            role=RoleType.MODERATOR,
        )
        updated_user.created_at = datetime.now()
        updated_user.updated_at = datetime.now()
        admin_service.repository.update_user_role.return_value = updated_user

        with patch("app.admin.service.clear_user_role_cache", new_callable=AsyncMock):
            result = await admin_service.assign_role(request, assigned_by_id=2)

        assert result.role == "Moderator"  # Should match schema pattern
        assert result.id == 1
        assert result.username == "testuser"
        admin_service.repository.get_user_by_id.assert_called_once_with(1)
        admin_service.repository.update_user_role.assert_called_once()

    async def test_assign_role_user_not_found(self, admin_service):
        """Test assigning role when user doesn't exist."""
        request = AssignRoleRequest(user_id=999, role="Moderator")
        admin_service.repository.get_user_by_id.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await admin_service.assign_role(request, assigned_by_id=2)

        assert "User not found" in str(exc_info.value)

    async def test_toggle_user_activate(self, admin_service, test_user):
        """Test activating a deactivated user."""
        from datetime import datetime

        inactive_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            is_active=False,
            role=RoleType.USER,
        )
        inactive_user.created_at = datetime.now()
        inactive_user.updated_at = datetime.now()
        admin_service.repository.get_user_by_id.return_value = inactive_user

        activated_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            is_active=True,
            role=RoleType.USER,
        )
        activated_user.created_at = datetime.now()
        activated_user.updated_at = datetime.now()
        admin_service.repository.toggle_user.return_value = activated_user

        result = await admin_service.toggle_user(user_id=1)

        assert result.is_active is True
        assert result.id == 1
        admin_service.repository.get_user_by_id.assert_called_once_with(1)
        admin_service.repository.toggle_user.assert_called_once()

    async def test_toggle_user_deactivate(self, admin_service, test_user):
        """Test deactivating an active user."""
        from datetime import datetime

        admin_service.repository.get_user_by_id.return_value = test_user

        deactivated_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            is_active=False,
            role=RoleType.USER,
        )
        deactivated_user.created_at = datetime.now()
        deactivated_user.updated_at = datetime.now()
        admin_service.repository.toggle_user.return_value = deactivated_user

        result = await admin_service.toggle_user(user_id=1)

        assert result.is_active is False
        assert result.id == 1

    async def test_toggle_user_not_found(self, admin_service):
        """Test toggling user that doesn't exist."""
        admin_service.repository.get_user_by_id.return_value = None

        with pytest.raises(UserNotFoundException) as exc_info:
            await admin_service.toggle_user(user_id=999)

        assert "User not found" in str(exc_info.value)

    async def test_get_dashboard_analytics_success(self, admin_service):
        """Test getting dashboard analytics successfully."""
        # Mock repository responses
        admin_service.repository.get_user_stats_by_role.return_value = (100, 2, 5, 93)
        admin_service.repository.get_total_posts.return_value = 250
        admin_service.repository.get_user_with_most_posts.return_value = (
            1,
            "topuser",
            "/path/to/image.jpg",
            50,
        )
        admin_service.repository.get_top_mentioned_users.return_value = [
            (1, "user1", "/path/img1.jpg", 100),
            (2, "user2", "/path/img2.jpg", 75),
        ]
        admin_service.repository.get_top_tags.return_value = [
            (1, "python", 150),
            (2, "javascript", 120),
        ]
        admin_service.repository.get_top_reported_users.return_value = []

        with patch("app.admin.service.ws_manager") as mock_ws_manager:
            mock_ws_manager.active_connections = {1: None, 2: None}
            result = await admin_service.get_dashboard_analytics()

        assert result.total_users == 100
        assert result.admin_count == 2
        assert result.moderator_count == 5
        assert result.normal_user_count == 93
        assert result.active_users == 2
        assert result.total_posts == 250
        assert result.user_with_most_posts.username == "topuser"
        assert len(result.top_5_mentioned_users) == 2
        assert len(result.top_5_tags) == 2

    async def test_get_dashboard_analytics_no_top_poster(self, admin_service):
        """Test dashboard analytics when no posts exist."""
        admin_service.repository.get_user_stats_by_role.return_value = (10, 1, 0, 9)
        admin_service.repository.get_total_posts.return_value = 0
        admin_service.repository.get_user_with_most_posts.return_value = None
        admin_service.repository.get_top_mentioned_users.return_value = []
        admin_service.repository.get_top_tags.return_value = []
        admin_service.repository.get_top_reported_users.return_value = []

        with patch("app.admin.service.ws_manager") as mock_ws_manager:
            mock_ws_manager.active_connections = {}
            result = await admin_service.get_dashboard_analytics()

        assert result.total_posts == 0
        assert result.user_with_most_posts is None
        assert len(result.top_5_mentioned_users) == 0
        assert len(result.top_5_tags) == 0
