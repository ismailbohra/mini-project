# app/posts/service.py
from typing import List

from app.posts.interface import PostRepositoryInterface
from app.posts.model import Posts
from app.posts.schema import (
    PostCreate,
    PostLikeResponse,
    PostReportResponse,
    PostResponse,
    PostUpdate,
    TagResponse,
)
from app.utils.exceptions import ForbiddenException, NotFoundException


class PostService:
    """Service for post business logic."""

    def __init__(self, repository: PostRepositoryInterface):
        self.repository = repository

    async def create_post(self, author_id: int, post_data: PostCreate) -> PostResponse:
        """Create a new post with tags."""
        # Create the post
        post = await self.repository.create_post(
            author_id=author_id,
            title=post_data.title,
            description=post_data.description,
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
        return self._post_to_response(post_with_tags)

    async def get_post(self, post_id: int) -> PostResponse:
        """Get a post by ID."""
        post = await self.repository.get_post_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with id {post_id} not found")
        return self._post_to_response(post)

    async def get_user_posts(
        self, author_id: int, skip: int = 0, limit: int = 100
    ) -> List[PostResponse]:
        """Get all posts by a user."""
        posts = await self.repository.get_posts_by_author(author_id, skip, limit)
        return [self._post_to_response(post) for post in posts]

    async def get_all_posts(
        self, skip: int = 0, limit: int = 100
    ) -> List[PostResponse]:
        """Get all posts."""
        posts = await self.repository.get_all_posts(skip, limit)
        return [self._post_to_response(post) for post in posts]

    async def update_post(
        self, post_id: int, author_id: int, post_data: PostUpdate
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
            post, title=post_data.title, description=post_data.description
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
        return self._post_to_response(updated_post)

    async def delete_post(self, post_id: int, author_id: int) -> None:
        """Delete a post."""
        post = await self.repository.get_post_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with id {post_id} not found")

        # Check if user is the author
        if post.author_id != author_id:
            raise ForbiddenException("You can only delete your own posts")

        await self.repository.delete_post(post)

    def _post_to_response(self, post: Posts) -> PostResponse:
        """Convert Post model to PostResponse."""
        # Extract tags from post_tags relationship
        tags = [TagResponse(id=pt.tag.id, name=pt.tag.name) for pt in post.tags]

        return PostResponse(
            id=post.id,
            author_id=post.author_id,
            title=post.title,
            description=post.description,
            tags=tags,
            created_at=post.created_at,
            updated_at=post.updated_at,
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