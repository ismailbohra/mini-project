"""
Unit tests for the comments module.

Tests:
- Create comment
- Get comment by ID
- Get comments for post
- Update comment
- Delete comment
- Like/unlike comment
- Report comment
- Reply to comment
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.comments.model import Comment
from app.comments.schema import CommentCreate, CommentUpdate
from app.comments.service import CommentService
from app.users.model import RoleType, User
from app.utils.exceptions import ForbiddenException, NotFoundException


@pytest.fixture
def mock_comment_repository():
    """Create a mock comment repository."""
    repository = AsyncMock()
    return repository


@pytest.fixture
def comment_service(mock_comment_repository):
    """Create a CommentService instance with mock repository."""
    return CommentService(mock_comment_repository)


@pytest.fixture
def test_comment():
    """Create a test comment."""
    from datetime import datetime

    comment = MagicMock(spec=Comment)
    comment.id = 1
    comment.title = "Test Comment"
    comment.description = "This is a test comment"
    comment.post_id = 1
    comment.author_id = 1
    comment.parent_comment_id = None
    comment.like_count = 0
    comment.reply_count = 0
    comment.created_at = datetime.now()
    comment.updated_at = datetime.now()
    comment.author = MagicMock()
    comment.author.id = 1
    comment.author.username = "testuser"
    comment.author.email = "test@example.com"
    comment.author.profile_image = None
    return comment


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
class TestCommentService:
    """Test cases for CommentService."""

    async def test_create_comment_success(self, comment_service, test_comment):
        """Test creating a comment successfully."""
        comment_data = CommentCreate(
            post_id=1, title="New Comment", description="New comment description"
        )

        comment_service.repository.create_comment.return_value = test_comment
        comment_service.repository.get_comment_by_id.return_value = test_comment
        comment_service.repository.get_mentioned_users.return_value = []
        comment_service.repository.check_if_user_liked_comment.return_value = False
        comment_service.repository.increment_post_comment_count = AsyncMock(
            return_value=None
        )
        comment_service.repository.get_user_by_username = AsyncMock(return_value=None)
        comment_service.repository.add_mention_to_comment = AsyncMock(return_value=None)

        # Mock AsyncSessionLocal for fetching post in non-reply comments
        mock_session = AsyncMock()
        mock_post_repo = MagicMock()
        mock_post = MagicMock()
        mock_post.author_id = 1
        mock_post_repo.get_post_by_id = AsyncMock(return_value=mock_post)

        with (
            patch("app.comments.service.redis_utils") as mock_redis,
            patch("app.comments.service.event_bus_module") as mock_event_bus,
            patch("app.comments.service.extract_mentions") as mock_extract,
            patch("app.config.database.AsyncSessionLocal") as mock_session_local,
            patch("app.posts.repository.PostRepository") as mock_repo_class,
        ):
            mock_redis.delete_pattern = AsyncMock()
            mock_redis.delete_cache = AsyncMock()
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()
            mock_event_bus.event_bus = None
            mock_extract.return_value = []
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_repo_class.return_value = mock_post_repo

            result = await comment_service.create_comment(
                author_id=1, comment_data=comment_data, current_user_id=1
            )

        assert result.title == "Test Comment"
        comment_service.repository.create_comment.assert_called_once()

    async def test_create_reply_comment_success(self, comment_service, test_comment):
        """Test creating a reply to a comment."""
        parent_comment = MagicMock(spec=Comment)
        parent_comment.id = 1
        parent_comment.post_id = 1

        comment_data = CommentCreate(
            post_id=1,
            title="Reply Comment",
            description="This is a reply",
            parent_comment_id=1,
        )

        comment_service.repository.get_comment_by_id.side_effect = [
            parent_comment,  # For parent validation
            test_comment,  # For fetching created comment
        ]
        comment_service.repository.create_comment.return_value = test_comment
        comment_service.repository.get_mentioned_users.return_value = []
        comment_service.repository.check_if_user_liked_comment.return_value = False
        comment_service.repository.increment_parent_comment_reply_count = AsyncMock(
            return_value=None
        )
        comment_service.repository.increment_post_comment_count = AsyncMock(
            return_value=None
        )
        comment_service.repository.get_user_by_username = AsyncMock(return_value=None)
        comment_service.repository.add_mention_to_comment = AsyncMock(return_value=None)

        with (
            patch("app.comments.service.redis_utils") as mock_redis,
            patch("app.comments.service.event_bus_module") as mock_event_bus,
            patch("app.comments.service.extract_mentions") as mock_extract,
        ):
            mock_redis.delete_pattern = AsyncMock()
            mock_redis.delete_cache = AsyncMock()
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()
            mock_event_bus.event_bus = None
            mock_extract.return_value = []

            result = await comment_service.create_comment(
                author_id=1, comment_data=comment_data, current_user_id=1
            )

        assert result is not None

    async def test_create_reply_parent_not_found(self, comment_service):
        """Test creating a reply when parent comment doesn't exist."""
        comment_data = CommentCreate(
            post_id=1,
            title="Reply Comment",
            description="This is a reply",
            parent_comment_id=999,
        )

        comment_service.repository.get_comment_by_id.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await comment_service.create_comment(
                author_id=1, comment_data=comment_data, current_user_id=1
            )

        assert "Parent comment with id 999 not found" in str(exc_info.value)

    async def test_create_reply_wrong_post(self, comment_service):
        """Test creating a reply when parent belongs to different post."""
        parent_comment = MagicMock(spec=Comment)
        parent_comment.id = 1
        parent_comment.post_id = 2  # Different post

        comment_data = CommentCreate(
            post_id=1,
            title="Reply Comment",
            description="This is a reply",
            parent_comment_id=1,
        )

        comment_service.repository.get_comment_by_id.return_value = parent_comment

        with pytest.raises(ForbiddenException) as exc_info:
            await comment_service.create_comment(
                author_id=1, comment_data=comment_data, current_user_id=1
            )

        assert "Parent comment must belong to same post" in str(exc_info.value)

    async def test_get_post_comments_success(self, comment_service, test_comment):
        """Test getting all comments for a post."""
        comment_service.repository.get_comments_by_post.return_value = [test_comment]
        comment_service.repository.get_mentioned_users.return_value = []
        comment_service.repository.check_if_user_liked_comment.return_value = False

        with patch("app.comments.service.redis_utils") as mock_redis:
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()

            result = await comment_service.get_post_comments(
                post_id=1, skip=0, limit=10, current_user_id=1
            )

        assert len(result) == 1
        assert result[0].title == "Test Comment"

    async def test_update_comment_success(self, comment_service, test_comment):
        """Test updating a comment by the author."""
        comment_data = CommentUpdate(
            title="Updated Comment", description="Updated description"
        )

        comment_service.repository.get_comment_by_id.return_value = test_comment
        comment_service.repository.update_comment.return_value = test_comment
        comment_service.repository.get_mentioned_users.return_value = []
        comment_service.repository.check_if_user_liked_comment.return_value = False
        comment_service.repository.remove_mentions_from_comment = AsyncMock(
            return_value=None
        )
        comment_service.repository.get_user_by_username = AsyncMock(return_value=None)
        comment_service.repository.add_mention_to_comment = AsyncMock(return_value=None)

        with (
            patch("app.comments.service.redis_utils") as mock_redis,
            patch("app.comments.service.extract_mentions") as mock_extract,
        ):
            mock_redis.delete_cache = AsyncMock()
            mock_redis.delete_pattern = AsyncMock()
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()
            mock_extract.return_value = []

            result = await comment_service.update_comment(
                comment_id=1,
                author_id=1,
                comment_data=comment_data,
                current_user_id=1,
                user_role="USER",
            )

        assert result is not None
        comment_service.repository.update_comment.assert_called_once()

    async def test_update_comment_forbidden(self, comment_service, test_comment):
        """Test updating a comment by non-author without admin rights."""
        comment_data = CommentUpdate(title="Updated Comment")
        comment_service.repository.get_comment_by_id.return_value = test_comment

        with pytest.raises(ForbiddenException) as exc_info:
            await comment_service.update_comment(
                comment_id=1,
                author_id=2,  # Different user
                comment_data=comment_data,
                current_user_id=2,
                user_role="USER",
            )

        assert "You can only update your own comments" in str(exc_info.value)

    async def test_update_comment_as_moderator(self, comment_service, test_comment):
        """Test updating any comment as moderator."""
        comment_data = CommentUpdate(title="Moderator Updated Comment")

        comment_service.repository.get_comment_by_id.return_value = test_comment
        comment_service.repository.update_comment.return_value = test_comment
        comment_service.repository.get_mentioned_users.return_value = []
        comment_service.repository.check_if_user_liked_comment.return_value = False

        with patch("app.comments.service.redis_utils") as mock_redis:
            mock_redis.delete_cache = AsyncMock()
            mock_redis.delete_pattern = AsyncMock()
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()

            result = await comment_service.update_comment(
                comment_id=1,
                author_id=2,
                comment_data=comment_data,
                current_user_id=2,
                user_role="Moderator",
            )

        assert result is not None

    async def test_update_comment_not_found(self, comment_service):
        """Test updating a non-existent comment."""
        comment_data = CommentUpdate(title="Updated Comment")
        comment_service.repository.get_comment_by_id.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await comment_service.update_comment(
                comment_id=999,
                author_id=1,
                comment_data=comment_data,
                current_user_id=1,
            )

        assert "Comment with id 999 not found" in str(exc_info.value)

    async def test_create_comment_with_mentions(self, comment_service, test_comment):
        """Test creating a comment with mentions."""
        comment_data = CommentCreate(
            post_id=1,
            title="Comment with mentions",
            description="Hello @user1 and @user2",
        )

        comment_service.repository.create_comment.return_value = test_comment
        comment_service.repository.get_comment_by_id.return_value = test_comment
        comment_service.repository.get_mentioned_users.return_value = []
        comment_service.repository.check_if_user_liked_comment.return_value = False
        comment_service.repository.increment_post_comment_count = AsyncMock(
            return_value=None
        )
        comment_service.repository.get_user_by_username = AsyncMock(
            return_value=MagicMock()
        )
        comment_service.repository.add_mention_to_comment = AsyncMock(return_value=None)

        # Mock AsyncSessionLocal for fetching post in non-reply comments
        mock_session = AsyncMock()
        mock_post_repo = MagicMock()
        mock_post = MagicMock()
        mock_post.author_id = 1
        mock_post_repo.get_post_by_id = AsyncMock(return_value=mock_post)

        # Mock UserRepository for _process_mentions
        mock_user_repo = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 2
        mock_user.username = "testuser"
        mock_user_repo.get_by_usernames = AsyncMock(return_value=[mock_user])
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user)

        with (
            patch("app.comments.service.redis_utils") as mock_redis,
            patch("app.comments.service.event_bus_module") as mock_event_bus,
            patch("app.comments.service.extract_mentions") as mock_extract,
            patch("app.config.database.AsyncSessionLocal") as mock_session_local,
            patch("app.posts.repository.PostRepository") as mock_repo_class,
            patch("app.users.repository.UserRepository") as mock_user_repo_class,
        ):
            mock_redis.delete_pattern = AsyncMock()
            mock_redis.delete_cache = AsyncMock()
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()
            mock_event_bus.event_bus = None
            mock_extract.return_value = ["user1", "user2"]
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_repo_class.return_value = mock_post_repo
            mock_user_repo_class.return_value = mock_user_repo

            result = await comment_service.create_comment(
                author_id=1, comment_data=comment_data, current_user_id=1
            )

        assert result is not None
