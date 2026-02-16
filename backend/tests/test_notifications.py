"""
Unit tests for the notifications module.

Tests:
- Get user notifications
- Mark notification as read
- Mark all notifications as read
- Get unread count
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.notifications.model import Notification
from app.notifications.service import NotificationService
from app.users.model import RoleType, User
from app.utils.exceptions import NotFoundException


@pytest.fixture
def mock_notification_repository():
    """Create a mock notification repository."""
    repository = AsyncMock()
    return repository


@pytest.fixture
def notification_service(mock_notification_repository):
    """Create a NotificationService instance with mock repository."""
    return NotificationService(mock_notification_repository)


@pytest.fixture
def test_notification():
    """Create a test notification."""
    notification = MagicMock(spec=Notification)
    notification.id = 1
    notification.receiver_id = 1
    notification.actor_id = 2
    notification.type = "like"
    notification.post_id = 1
    notification.comment_id = None
    notification.is_read = False
    notification.actor = MagicMock()
    notification.actor.username = "actor_user"
    return notification


@pytest.fixture
def test_user():
    """Create a test user."""
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword",
        is_active=True,
        role=RoleType.USER,
    )
    return user


@pytest.mark.unit
@pytest.mark.asyncio
class TestNotificationService:
    """Test cases for NotificationService."""

    async def test_get_user_notifications_success(
        self, notification_service, test_notification
    ):
        """Test getting user notifications successfully."""
        notification_service.repository.get_user_notifications.return_value = [
            test_notification
        ]

        result = await notification_service.get_user_notifications(
            user_id=1, skip=0, limit=50
        )

        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].receiver_id == 1
        assert result[0].actor_username == "actor_user"
        notification_service.repository.get_user_notifications.assert_called_once_with(
            1, 0, 50
        )

    async def test_get_user_notifications_empty(self, notification_service):
        """Test getting notifications when none exist."""
        notification_service.repository.get_user_notifications.return_value = []

        result = await notification_service.get_user_notifications(
            user_id=1, skip=0, limit=50
        )

        assert len(result) == 0

    async def test_get_user_notifications_pagination(
        self, notification_service, test_notification
    ):
        """Test getting notifications with pagination."""
        notification_service.repository.get_user_notifications.return_value = [
            test_notification
        ]

        result = await notification_service.get_user_notifications(
            user_id=1, skip=10, limit=20
        )

        assert len(result) == 1
        notification_service.repository.get_user_notifications.assert_called_once_with(
            1, 10, 20
        )

    async def test_mark_as_read_success(self, notification_service, test_notification):
        """Test marking a notification as read successfully."""
        read_notification = MagicMock(spec=Notification)
        read_notification.id = 1
        read_notification.receiver_id = 1
        read_notification.actor_id = 2
        read_notification.type = "like"
        read_notification.post_id = 1
        read_notification.comment_id = None
        read_notification.is_read = True
        read_notification.actor = MagicMock()
        read_notification.actor.username = "actor_user"

        notification_service.repository.mark_as_read.return_value = read_notification

        with patch("app.notifications.service.redis_utils") as mock_redis:
            mock_redis.delete_cache = AsyncMock()

            result = await notification_service.mark_as_read(
                notification_id=1, user_id=1
            )

        assert result.is_read is True
        assert result.id == 1
        notification_service.repository.mark_as_read.assert_called_once_with(1, 1)
        mock_redis.delete_cache.assert_called_once_with("notifications:unread:1")

    async def test_mark_as_read_not_found(self, notification_service):
        """Test marking non-existent notification as read."""
        notification_service.repository.mark_as_read.return_value = None

        with patch("app.notifications.service.redis_utils") as mock_redis:
            mock_redis.delete_cache = AsyncMock()

            with pytest.raises(NotFoundException) as exc_info:
                await notification_service.mark_as_read(notification_id=999, user_id=1)

        assert "Notification not found" in str(exc_info.value)

    async def test_mark_all_as_read_success(self, notification_service):
        """Test marking all notifications as read successfully."""
        notification_service.repository.mark_all_as_read.return_value = None

        with patch("app.notifications.service.redis_utils") as mock_redis:
            mock_redis.delete_cache = AsyncMock()

            await notification_service.mark_all_as_read(user_id=1)

        notification_service.repository.mark_all_as_read.assert_called_once_with(1)
        mock_redis.delete_cache.assert_called_once_with("notifications:unread:1")

    async def test_get_unread_count_from_db(self, notification_service):
        """Test getting unread count from database."""
        notification_service.repository.get_unread_count.return_value = 5

        with patch("app.notifications.service.redis_utils") as mock_redis:
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()

            result = await notification_service.get_unread_count(user_id=1)

        assert result == 5
        notification_service.repository.get_unread_count.assert_called_once_with(1)
        mock_redis.get_cache.assert_called_once_with("notifications:unread:1")
        mock_redis.set_cache.assert_called_once_with(
            "notifications:unread:1", 5, expire=60
        )

    async def test_get_unread_count_from_cache(self, notification_service):
        """Test getting unread count from cache."""
        with patch("app.notifications.service.redis_utils") as mock_redis:
            mock_redis.get_cache = AsyncMock(return_value=10)

            result = await notification_service.get_unread_count(user_id=1)

        assert result == 10
        notification_service.repository.get_unread_count.assert_not_called()
        mock_redis.get_cache.assert_called_once_with("notifications:unread:1")

    async def test_get_unread_count_zero(self, notification_service):
        """Test getting unread count when zero."""
        notification_service.repository.get_unread_count.return_value = 0

        with patch("app.notifications.service.redis_utils") as mock_redis:
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()

            result = await notification_service.get_unread_count(user_id=1)

        assert result == 0
        mock_redis.set_cache.assert_called_once_with(
            "notifications:unread:1", 0, expire=60
        )

    async def test_notification_with_comment(self, notification_service):
        """Test notification related to a comment."""
        notification = MagicMock(spec=Notification)
        notification.id = 1
        notification.receiver_id = 1
        notification.actor_id = 2
        notification.type = "comment"
        notification.post_id = 1
        notification.comment_id = 5
        notification.is_read = False
        notification.actor = MagicMock()
        notification.actor.username = "commenter"

        notification_service.repository.get_user_notifications.return_value = [
            notification
        ]

        result = await notification_service.get_user_notifications(
            user_id=1, skip=0, limit=50
        )

        assert len(result) == 1
        assert result[0].comment_id == 5
        assert result[0].type == "comment"

    async def test_notification_without_actor(self, notification_service):
        """Test notification when actor is None."""
        notification = MagicMock(spec=Notification)
        notification.id = 1
        notification.receiver_id = 1
        notification.actor_id = 999  # Valid ID but actor deleted
        notification.type = "system"
        notification.post_id = None
        notification.comment_id = None
        notification.is_read = False
        notification.actor = None  # Actor deleted

        notification_service.repository.get_user_notifications.return_value = [
            notification
        ]

        result = await notification_service.get_user_notifications(
            user_id=1, skip=0, limit=50
        )

        assert len(result) == 1
        assert result[0].actor_username == "Unknown"
