# app/posts/service.py
from typing import List, Optional

import app.utils.event_bus as event_bus_module
import app.utils.redis as redis_utils
from app.posts.interface import PostRepositoryInterface
from app.posts.model import Posts
from app.posts.schema import (
    PostCreate,
    PostLikeResponse,
    PostListResponse,
    PostReportResponse,
    PostResponse,
    PostUpdate,
    TagResponse,
)
from app.utils.exceptions import ForbiddenException, NotFoundException
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PostService:
    """Service for post business logic."""

    def __init__(self, repository: PostRepositoryInterface):
        self.repository = repository

    async def create_post(
        self,
        author_id: int,
        post_data: PostCreate,
        current_user_id: Optional[int] = None,
        image_path: Optional[str] = None,
    ) -> PostResponse:
        """Create a new post with tags."""
        # Create the post
        post = await self.repository.create_post(
            author_id=author_id,
            title=post_data.title,
            description=post_data.description,
            image_path=image_path,
        )

        # Handle tags (get or create, case-insensitive)
        if post_data.tags:
            tags = []
            for tag_name in post_data.tags:
                tag = await self.repository.get_or_create_tag(tag_name)
                tags.append(tag)

            # Add tags to post
            await self.repository.add_tags_to_post(post, tags)

        # Fetch the post with tags to return
        post_with_tags = await self.repository.get_post_by_id(post.id)
        return await self._post_to_response(post_with_tags, current_user_id)

    async def get_post(
        self, post_id: int, current_user_id: Optional[int] = None
    ) -> PostResponse:
        """Get a post by ID."""
        cache_key = f"post:{post_id}"
        cached = await redis_utils.get_cache(cache_key)
        if cached:
            return PostResponse(**cached)

        post = await self.repository.get_post_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with id {post_id} not found")

        response = await self._post_to_response(post, current_user_id)

        await redis_utils.set_cache(cache_key, response.model_dump(mode="json"))

        return response

    async def get_user_posts(
        self,
        author_id: int,
        skip: int = 0,
        limit: int = 100,
        current_user_id: Optional[int] = None,
    ) -> PostListResponse:
        """Get all posts by a user with total count."""
        posts, total = await self.repository.get_posts_by_author(author_id, skip, limit)
        posts_response = [
            await self._post_to_response(post, current_user_id) for post in posts
        ]
        return PostListResponse(posts=posts_response, total=total)

    async def get_all_posts(
        self,
        skip: int = 0,
        limit: int = 100,
        current_user_id: Optional[int] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> PostListResponse:
        """Get all posts with search, filter, and sort, including total count."""
        posts, total = await self.repository.get_all_posts(
            skip, limit, search, tags, sort_by, sort_order
        )
        posts_response = [
            await self._post_to_response(post, current_user_id) for post in posts
        ]
        return PostListResponse(posts=posts_response, total=total)

    async def update_post(
        self,
        post_id: int,
        author_id: int,
        post_data: PostUpdate,
        current_user_id: Optional[int] = None,
        image_path: Optional[str] = None,
    ) -> PostResponse:
        """Update a post."""
        post = await self.repository.get_post_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with id {post_id} not found")

        # Check if user is the author
        if post.author_id != author_id:
            raise ForbiddenException("You can only update your own posts")

        # Update post fields
        post = await self.repository.update_post(
            post,
            title=post_data.title,
            description=post_data.description,
            image_path=image_path,
        )

        # Update tags if provided
        if post_data.tags is not None:
            # Remove existing tags
            await self.repository.remove_tags_from_post(post)

            # Add new tags
            if post_data.tags:
                tags = []
                for tag_name in post_data.tags:
                    tag = await self.repository.get_or_create_tag(tag_name)
                    tags.append(tag)
                await self.repository.add_tags_to_post(post, tags)

        # Fetch updated post with tags
        updated_post = await self.repository.get_post_by_id(post_id)

        await redis_utils.delete_cache(f"post:{post_id}")

        return await self._post_to_response(updated_post, current_user_id)

    async def delete_post(self, post_id: int, author_id: int) -> None:
        """Delete a post."""
        post = await self.repository.get_post_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with id {post_id} not found")

        # Check if user is the author
        if post.author_id != author_id:
            raise ForbiddenException("You can only delete your own posts")

        await self.repository.delete_post(post)

    async def _post_to_response(
        self, post: Posts, current_user_id: Optional[int] = None
    ) -> PostResponse:
        """Convert Post model to PostResponse."""
        # Extract tags from post_tags relationship
        tags = [TagResponse(id=pt.tag.id, name=pt.tag.name) for pt in post.tags]

        # Build author object
        author = post.author
        author_obj = None
        if author:
            author_obj = {
                "id": author.id,
                "username": author.username,
                "email": author.email,
            }

        # Get likes count
        likes_count = await self.repository.get_post_likes_count(post.id)
        comments_count = await self.repository.get_post_comments_count(post.id)

        # Check if current user has liked this post
        user_has_liked = False
        if current_user_id:
            like = await self.repository.get_post_like(current_user_id, post.id)
            user_has_liked = like is not None

        return PostResponse(
            id=post.id,
            author_id=post.author_id,
            author=author_obj,
            title=post.title,
            description=post.description,
            tags=tags,
            created_at=post.created_at,
            updated_at=post.updated_at,
            likes_count=likes_count,
            comments_count=comments_count,
            user_has_liked=user_has_liked,
            image_path=post.image_path,
        )

    async def like_post(self, user_id: int, post_id: int) -> PostLikeResponse:
        """Like a post."""
        # Check if post exists
        post = await self.repository.get_post_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with id {post_id} not found")

        # Check if already liked
        existing_like = await self.repository.get_post_like(user_id, post_id)
        if existing_like:
            raise ForbiddenException("You have already liked this post")

        like = await self.repository.add_post_like(user_id, post_id)

        # Emit event
        logger.debug(
            f"Publishing post.liked event - post_id: {post_id}, actor: {user_id}, author: {post.author_id}"
        )
        if event_bus_module.event_bus:
            await event_bus_module.event_bus.publish(
                "post.liked",
                {
                    "post_id": post_id,
                    "actor_id": user_id,
                    "post_author_id": post.author_id,
                },
            )
            logger.debug("post.liked event published successfully")
        else:
            logger.error("Event bus is None, cannot publish post.liked event")

        return PostLikeResponse(
            id=like.id,
            user_id=like.user_id,
            post_id=like.post_id,
            created_at=like.created_at,
        )

    async def unlike_post(self, user_id: int, post_id: int) -> None:
        """Unlike a post."""
        # Check if like exists
        existing_like = await self.repository.get_post_like(user_id, post_id)
        if not existing_like:
            raise NotFoundException("Like not found")

        await self.repository.remove_post_like(user_id, post_id)

    async def get_post_likes_count(self, post_id: int) -> int:
        """Get count of likes for a post."""
        return await self.repository.get_post_likes_count(post_id)

    async def report_post(
        self, user_id: int, post_id: int, reason: str
    ) -> PostReportResponse:
        """Report a post."""
        # Check if post exists
        post = await self.repository.get_post_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with id {post_id} not found")

        # Check if user already reported this post
        existing_report = await self.repository.get_post_report(user_id, post_id)
        if existing_report:
            raise ForbiddenException("You have already reported this post")

        report = await self.repository.create_post_report(user_id, post_id, reason)
        return PostReportResponse(
            id=report.id,
            user_id=report.user_id,
            post_id=report.post_id,
            reason=report.reason,
            status=report.status.value,
            created_at=report.created_at,
            reviewed_at=report.reviewed_at,
        )

    async def get_all_tags(self) -> List[TagResponse]:
        """Get all tags."""
        tags = await self.repository.get_all_tags()
        return [TagResponse(id=tag.id, name=tag.name) for tag in tags]

    async def search_suggestions(self, search: str, limit: int = 10) -> List[dict]:
        """Get search suggestions based on partial match."""
        if not search or len(search) < 2:
            return []
        return await self.repository.search_suggestions(search, limit)
