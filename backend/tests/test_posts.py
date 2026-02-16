"""
Unit tests for the posts module.

Tests:
- Create post
- Get post by ID
- Get user posts
- Get all posts
- Update post
- Delete post
- Like/unlike post
- Report post
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.posts.model import Posts
from app.posts.schema import PostCreate, PostListResponse, PostUpdate
from app.posts.service import PostService
from app.users.model import RoleType, User
from app.utils.exceptions import ForbiddenException, NotFoundException


@pytest.fixture
def mock_post_repository():
    """Create a mock post repository."""
    repository = AsyncMock()
    return repository


@pytest.fixture
def post_service(mock_post_repository):
    """Create a PostService instance with mock repository."""
    return PostService(mock_post_repository)


@pytest.fixture
def test_post():
    """Create a test post."""
    from datetime import datetime

    post = MagicMock(spec=Posts)
    post.id = 1
    post.title = "Test Post"
    post.description = "This is a test post"
    post.author_id = 1
    post.image_path = None
    post.like_count = 0
    post.comment_count = 0
    post.tags = []
    post.created_at = datetime.now()
    post.updated_at = datetime.now()
    # Mock author as a proper object, not nested MagicMock
    post.author = MagicMock()
    post.author.id = 1
    post.author.username = "testuser"
    post.author.email = "test@example.com"
    post.author.profile_image = None
    return post


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
class TestPostService:
    """Test cases for PostService."""

    async def test_create_post_success(self, post_service, test_post):
        """Test creating a post successfully."""
        post_data = PostCreate(
            title="New Post",
            description="New post description",
            tags=["python", "testing"],
        )

        post_service.repository.create_post.return_value = test_post
        post_service.repository.get_or_create_tag.return_value = MagicMock()
        post_service.repository.add_tags_to_post = AsyncMock(return_value=None)
        post_service.repository.get_post_by_id.return_value = test_post
        post_service.repository.get_mentioned_users.return_value = []
        post_service.repository.check_if_user_liked_post.return_value = False
        post_service.repository.get_user_by_username = AsyncMock(return_value=None)
        post_service.repository.add_mention_to_post = AsyncMock(return_value=None)

        with (
            patch("app.posts.service.redis_utils") as mock_redis,
            patch("app.posts.service.event_bus_module") as mock_event_bus,
            patch("app.posts.service.extract_mentions") as mock_extract,
        ):
            mock_redis.delete_pattern = AsyncMock()
            mock_redis.delete_cache = AsyncMock()
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()
            mock_event_bus.event_bus = AsyncMock()
            mock_event_bus.event_bus.publish = AsyncMock()
            mock_extract.return_value = []

            result = await post_service.create_post(
                author_id=1, post_data=post_data, current_user_id=1
            )

        assert result.title == "Test Post"
        post_service.repository.create_post.assert_called_once()

    async def test_create_post_with_mentions(self, post_service, test_post):
        """Test creating a post with user mentions."""
        post_data = PostCreate(
            title="New Post", description="Hello @user1 and @user2", tags=[]
        )

        post_service.repository.create_post.return_value = test_post
        post_service.repository.get_post_by_id.return_value = test_post
        post_service.repository.get_mentioned_users.return_value = []
        post_service.repository.check_if_user_liked_post.return_value = False
        post_service.repository.get_user_by_username = AsyncMock(
            return_value=MagicMock()
        )
        post_service.repository.add_mention_to_post = AsyncMock(return_value=None)
        post_service.repository.add_mentions_to_post = AsyncMock(return_value=None)

        # Mock AsyncSessionLocal for fetching users in _process_mentions
        mock_session = AsyncMock()
        mock_user_repo = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 2
        mock_user.username = "testuser"
        mock_user_repo.get_by_usernames = AsyncMock(return_value=[mock_user])
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user)

        with (
            patch("app.posts.service.redis_utils") as mock_redis,
            patch("app.posts.service.event_bus_module") as mock_event_bus,
            patch("app.posts.service.extract_mentions") as mock_extract,
            patch("app.config.database.AsyncSessionLocal") as mock_session_local,
            patch("app.users.repository.UserRepository") as mock_user_repo_class,
        ):
            mock_redis.delete_pattern = AsyncMock()
            mock_redis.delete_cache = AsyncMock()
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()
            mock_event_bus.event_bus = None
            mock_extract.return_value = ["user1", "user2"]
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_user_repo_class.return_value = mock_user_repo

            result = await post_service.create_post(
                author_id=1, post_data=post_data, current_user_id=1
            )

        assert result is not None

    async def test_get_post_success(self, post_service, test_post):
        """Test getting a post by ID successfully."""
        post_service.repository.get_post_by_id.return_value = test_post
        post_service.repository.get_mentioned_users.return_value = []
        post_service.repository.check_if_user_liked_post.return_value = False

        with patch("app.posts.service.redis_utils") as mock_redis:
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()

            result = await post_service.get_post(post_id=1, current_user_id=1)

        assert result.id == 1
        assert result.title == "Test Post"
        post_service.repository.get_post_by_id.assert_called_once_with(1)

    async def test_get_post_not_found(self, post_service):
        """Test getting a non-existent post."""
        post_service.repository.get_post_by_id.return_value = None

        with patch("app.posts.service.redis_utils") as mock_redis:
            mock_redis.get_cache = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException) as exc_info:
                await post_service.get_post(post_id=999, current_user_id=1)

        assert "Post with id 999 not found" in str(exc_info.value)

    async def test_get_post_from_cache(self, post_service):
        """Test getting a post from cache."""
        from datetime import datetime

        cached_data = {
            "id": 1,
            "title": "Cached Post",
            "description": "From cache",
            "author_id": 1,
            "author": {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "profile_image": None,
            },
            "author_username": "testuser",
            "author_profile_image": None,
            "image_path": None,
            "like_count": 5,
            "comment_count": 2,
            "is_liked": False,
            "tags": [],
            "mentioned_users": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        with patch("app.posts.service.redis_utils") as mock_redis:
            mock_redis.get_cache = AsyncMock(return_value=cached_data)

            result = await post_service.get_post(post_id=1, current_user_id=1)

        assert result.title == "Cached Post"
        post_service.repository.get_post_by_id.assert_not_called()

    async def test_get_user_posts_success(self, post_service, test_post):
        """Test getting all posts by a user."""
        post_service.repository.get_posts_by_author.return_value = ([test_post], 1)
        post_service.repository.get_mentioned_users.return_value = []
        post_service.repository.check_if_user_liked_post.return_value = False

        with patch("app.posts.service.redis_utils") as mock_redis:
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()

            result = await post_service.get_user_posts(
                author_id=1, skip=0, limit=10, current_user_id=1
            )

        assert isinstance(result, PostListResponse)
        assert len(result.posts) == 1
        assert result.total == 1

    async def test_get_all_posts_success(self, post_service, test_post):
        """Test getting all posts with filters."""
        post_service.repository.get_all_posts.return_value = ([test_post], 1)
        post_service.repository.get_mentioned_users.return_value = []
        post_service.repository.check_if_user_liked_post.return_value = False

        result = await post_service.get_all_posts(
            skip=0,
            limit=10,
            current_user_id=1,
            search="test",
            tags=["python"],
            sort_by="created_at",
            sort_order="desc",
        )

        assert len(result.posts) == 1
        assert result.total == 1

    async def test_update_post_success(self, post_service, test_post):
        """Test updating a post by the author."""
        post_data = PostUpdate(title="Updated Post", description="Updated description")

        post_service.repository.get_post_by_id.return_value = test_post
        post_service.repository.update_post.return_value = test_post
        post_service.repository.get_mentioned_users.return_value = []
        post_service.repository.check_if_user_liked_post.return_value = False
        post_service.repository.remove_mentions_from_post = AsyncMock(return_value=None)

        with (
            patch("app.posts.service.redis_utils") as mock_redis,
            patch("app.posts.service.extract_mentions") as mock_extract,
        ):
            mock_redis.delete_cache = AsyncMock()
            mock_redis.delete_pattern = AsyncMock()
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()
            mock_extract.return_value = []

            result = await post_service.update_post(
                post_id=1,
                author_id=1,
                post_data=post_data,
                current_user_id=1,
                user_role="USER",
            )

        assert result is not None
        post_service.repository.update_post.assert_called_once()

    async def test_update_post_forbidden(self, post_service, test_post):
        """Test updating a post by non-author without admin rights."""
        post_data = PostUpdate(title="Updated Post")
        post_service.repository.get_post_by_id.return_value = test_post

        with pytest.raises(ForbiddenException) as exc_info:
            await post_service.update_post(
                post_id=1,
                author_id=2,  # Different user
                post_data=post_data,
                current_user_id=2,
                user_role="USER",
            )

        assert "You can only update your own posts" in str(exc_info.value)

    async def test_update_post_as_admin(self, post_service, test_post):
        """Test updating any post as admin."""
        post_data = PostUpdate(title="Admin Updated Post")

        post_service.repository.get_post_by_id.return_value = test_post
        post_service.repository.update_post.return_value = test_post
        post_service.repository.get_mentioned_users.return_value = []
        post_service.repository.check_if_user_liked_post.return_value = False

        with patch("app.posts.service.redis_utils") as mock_redis:
            mock_redis.delete_cache = AsyncMock()
            mock_redis.delete_pattern = AsyncMock()
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()

            result = await post_service.update_post(
                post_id=1,
                author_id=2,  # Different user
                post_data=post_data,
                current_user_id=2,
                user_role="Admin",  # But admin role
            )

        assert result is not None
        post_service.repository.update_post.assert_called_once()

    async def test_update_post_not_found(self, post_service):
        """Test updating a non-existent post."""
        post_data = PostUpdate(title="Updated Post")
        post_service.repository.get_post_by_id.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await post_service.update_post(
                post_id=999, author_id=1, post_data=post_data, current_user_id=1
            )

        assert "Post with id 999 not found" in str(exc_info.value)

    async def test_update_post_with_tags(self, post_service, test_post):
        """Test updating post tags."""
        post_data = PostUpdate(title="Updated Post", tags=["newtag1", "newtag2"])

        post_service.repository.get_post_by_id.return_value = test_post
        post_service.repository.update_post.return_value = test_post
        post_service.repository.remove_tags_from_post = AsyncMock(return_value=None)
        post_service.repository.get_or_create_tag.return_value = MagicMock()
        post_service.repository.add_tags_to_post = AsyncMock(return_value=None)
        post_service.repository.get_mentioned_users.return_value = []
        post_service.repository.check_if_user_liked_post.return_value = False

        with patch("app.posts.service.redis_utils") as mock_redis:
            mock_redis.delete_cache = AsyncMock()
            mock_redis.delete_pattern = AsyncMock()
            mock_redis.get_cache = AsyncMock(return_value=None)
            mock_redis.set_cache = AsyncMock()

            result = await post_service.update_post(
                post_id=1,
                author_id=1,
                post_data=post_data,
                current_user_id=1,
                user_role="USER",
            )

        assert result is not None
        post_service.repository.remove_tags_from_post.assert_called_once()
        assert post_service.repository.get_or_create_tag.call_count == 2
