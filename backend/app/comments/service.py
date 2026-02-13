# app/comments/service.py
from typing import List, Optional

import app.utils.event_bus as event_bus_module
import app.utils.redis as redis_utils
from app.comments.interface import CommentRepositoryInterface
from app.comments.model import Comment
from app.comments.schema import (
    CommentCreate,
    CommentLikeResponse,
    CommentReportResponse,
    CommentResponse,
    CommentUpdate,
    MentionedUserResponse,
)
from app.utils.exceptions import ForbiddenException, NotFoundException
from app.utils.logging import get_logger
from app.utils.mentions import extract_mentions

logger = get_logger(__name__)


class CommentService:
    """Service for comment business logic."""

    def __init__(self, repository: CommentRepositoryInterface):
        self.repository = repository

    async def create_comment(
        self,
        author_id: int,
        comment_data: CommentCreate,
        current_user_id: Optional[int] = None,
    ) -> CommentResponse:
        """Create a new comment."""
        # Validate parent comment exists if provided
        if comment_data.parent_comment_id:
            parent = await self.repository.get_comment_by_id(
                comment_data.parent_comment_id
            )
            if not parent:
                raise NotFoundException(
                    f"Parent comment with id {comment_data.parent_comment_id} not found"
                )
            # Ensure parent belongs to same post
            if parent.post_id != comment_data.post_id:
                raise ForbiddenException("Parent comment must belong to same post")

        comment = await self.repository.create_comment(
            author_id=author_id,
            post_id=comment_data.post_id,
            title=comment_data.title,
            description=comment_data.description,
            parent_comment_id=comment_data.parent_comment_id,
        )

        # Handle mentions
        await self._process_mentions(
            comment_data.post_id, comment.id, comment_data.description, author_id
        )

        # The repository now returns the comment with the `author` relationship loaded
        comment_with_author = comment

        await redis_utils.delete_cache(f"post:{comment_data.post_id}")
        await redis_utils.delete_cache(f"comments:post:{comment_data.post_id}")

        # Emit event
        if comment_data.parent_comment_id:
            # `parent` was already fetched earlier during validation; reuse it
            if event_bus_module.event_bus:
                await event_bus_module.event_bus.publish(
                    "comment.replied",
                    {
                        "post_id": comment_data.post_id,
                        "comment_id": comment.id,
                        "actor_id": author_id,
                        "parent_author_id": parent.author_id,
                    },
                )
        else:
            from app.config.database import AsyncSessionLocal
            from app.posts.repository import PostRepository

            async with AsyncSessionLocal() as session:
                post_repo = PostRepository(session)
                post = await post_repo.get_post_by_id(comment_data.post_id)
                if post and event_bus_module.event_bus:
                    await event_bus_module.event_bus.publish(
                        "comment.created",
                        {
                            "post_id": comment_data.post_id,
                            "comment_id": comment.id,
                            "actor_id": author_id,
                            "post_author_id": post.author_id,
                        },
                    )

        if event_bus_module.event_bus:
            await event_bus_module.event_bus.publish(
                "comment.state.updated",
                {
                    "post_id": comment_data.post_id,
                    "comment_id": comment.id,
                    "actor_id": author_id,
                },
            )

        return await self._comment_to_response(comment_with_author, current_user_id)

    async def get_comment(
        self, comment_id: int, current_user_id: Optional[int] = None
    ) -> CommentResponse:
        """Get a comment by ID with nested replies."""
        comment = await self.repository.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment with id {comment_id} not found")
        return await self._comment_to_response(comment, current_user_id)

    async def get_post_comments(
        self,
        post_id: int,
        skip: int = 0,
        limit: int = 100,
        current_user_id: Optional[int] = None,
    ) -> List[CommentResponse]:
        """Get all top-level comments for a post with nested replies."""
        cache_key = f"comments:post:{post_id}"
        cached = await redis_utils.get_cache(cache_key)
        if cached:
            return [CommentResponse(**item) for item in cached]

        comments = await self.repository.get_comments_by_post(post_id, skip, limit)
        response = [
            await self._comment_to_response(comment, current_user_id)
            for comment in comments
        ]

        await redis_utils.set_cache(
            cache_key, [r.model_dump(mode="json") for r in response]
        )

        return response

    async def update_comment(
        self,
        comment_id: int,
        author_id: int,
        comment_data: CommentUpdate,
        current_user_id: Optional[int] = None,
        user_role: Optional[str] = None,
    ) -> CommentResponse:
        """Update a comment."""
        comment = await self.repository.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment with id {comment_id} not found")

        # Check if user is the author or has admin/moderator role
        from app.auth.model import RoleType

        is_admin_or_moderator = user_role in [
            RoleType.ADMIN.value,
            RoleType.MODERATOR.value,
        ]
        if comment.author_id != author_id and not is_admin_or_moderator:
            raise ForbiddenException("You can only update your own comments")

        comment = await self.repository.update_comment(
            comment, title=comment_data.title, description=comment_data.description
        )

        # Handle mentions when description is being updated
        if comment_data.description is not None:
            # Remove existing mentions and add new ones
            await self.repository.remove_mentions_from_comment(comment_id)
            await self._process_mentions(
                comment.post_id, comment_id, comment_data.description, author_id
            )

        await redis_utils.delete_cache(f"post:{comment.post_id}")
        await redis_utils.delete_cache(f"comments:post:{comment.post_id}")

        # The repository returns the updated comment with `author` loaded
        return await self._comment_to_response(comment, current_user_id)

    async def delete_comment(
        self, comment_id: int, author_id: int, user_role: Optional[str] = None
    ) -> None:
        """Delete a comment."""
        comment = await self.repository.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment with id {comment_id} not found")

        # Check if user is the author or has admin/moderator role
        from app.auth.model import RoleType

        is_admin_or_moderator = user_role in [
            RoleType.ADMIN.value,
            RoleType.MODERATOR.value,
        ]
        if comment.author_id != author_id and not is_admin_or_moderator:
            raise ForbiddenException("You can only delete your own comments")

        post_id = comment.post_id
        await self.repository.delete_comment(comment)

        await redis_utils.delete_cache(f"post:{post_id}")
        await redis_utils.delete_cache(f"comments:post:{post_id}")

        if event_bus_module.event_bus:
            await event_bus_module.event_bus.publish(
                "comment.deleted",
                {
                    "post_id": post_id,
                    "comment_id": comment_id,
                    "actor_id": author_id,
                },
            )

    async def like_comment(self, user_id: int, comment_id: int) -> CommentLikeResponse:
        """Like a comment."""
        # Check if comment exists
        comment = await self.repository.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment with id {comment_id} not found")

        # Check if already liked
        existing_like = await self.repository.get_comment_like(user_id, comment_id)
        if existing_like:
            raise ForbiddenException("You have already liked this comment")

        like = await self.repository.add_comment_like(user_id, comment_id)

        await redis_utils.delete_cache(f"post:{comment.post_id}")
        await redis_utils.delete_cache(f"comments:post:{comment.post_id}")

        # Emit event
        logger.debug(
            f"Publishing comment.liked event - comment_id: {comment_id}, actor: {user_id}, author: {comment.author_id}"
        )
        if event_bus_module.event_bus:
            await event_bus_module.event_bus.publish(
                "comment.liked",
                {
                    "post_id": comment.post_id,
                    "comment_id": comment_id,
                    "actor_id": user_id,
                    "comment_author_id": comment.author_id,
                },
            )
            await event_bus_module.event_bus.publish(
                "comment.state.updated",
                {
                    "post_id": comment.post_id,
                    "comment_id": comment_id,
                    "actor_id": user_id,
                },
            )
            logger.debug("comment.liked event published successfully")
        else:
            logger.error("Event bus is None, cannot publish comment.liked event")

        return CommentLikeResponse(
            id=like.id,
            user_id=like.user_id,
            comment_id=like.comment_id,
            created_at=like.created_at,
        )

    async def unlike_comment(self, user_id: int, comment_id: int) -> None:
        """Unlike a comment."""
        # Check if like exists
        existing_like = await self.repository.get_comment_like(user_id, comment_id)
        if not existing_like:
            raise NotFoundException("Like not found")

        comment = await self.repository.get_comment_by_id(comment_id)
        await self.repository.remove_comment_like(user_id, comment_id)

        if comment:
            await redis_utils.delete_cache(f"post:{comment.post_id}")
            await redis_utils.delete_cache(f"comments:post:{comment.post_id}")

            if event_bus_module.event_bus:
                await event_bus_module.event_bus.publish(
                    "comment.unliked",
                    {
                        "post_id": comment.post_id,
                        "comment_id": comment_id,
                        "actor_id": user_id,
                    },
                )
                await event_bus_module.event_bus.publish(
                    "comment.state.updated",
                    {
                        "post_id": comment.post_id,
                        "comment_id": comment_id,
                        "actor_id": user_id,
                    },
                )

    async def report_comment(
        self, user_id: int, comment_id: int, reason: str
    ) -> CommentReportResponse:
        """Report a comment."""
        # Check if comment exists
        comment = await self.repository.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment with id {comment_id} not found")

        # Check if user already reported this comment
        existing_report = await self.repository.get_comment_report(user_id, comment_id)
        if existing_report:
            raise ForbiddenException("You have already reported this comment")

        report = await self.repository.create_comment_report(
            user_id, comment_id, reason
        )
        return CommentReportResponse(
            id=report.id,
            user_id=report.user_id,
            comment_id=report.comment_id,
            reason=report.reason,
            status=report.status.value,
            created_at=report.created_at,
            reviewed_at=report.reviewed_at,
        )

    async def _comment_to_response(
        self, comment: Comment, current_user_id: Optional[int] = None
    ) -> CommentResponse:
        """Convert Comment model to CommentResponse with nested replies."""
        # Get likes count
        likes_count = await self.repository.get_comment_likes_count(comment.id)

        # Check if current user has liked this comment
        user_has_liked = False
        if current_user_id:
            like = await self.repository.get_comment_like(current_user_id, comment.id)
            user_has_liked = like is not None

        # Get mentioned users
        mentions = await self.repository.get_comment_mentions(comment.id)
        mentioned_users = [
            MentionedUserResponse(
                id=mention.user.id,
                username=mention.user.username,
                profile_image=mention.user.profile_image,
            )
            for mention in mentions
        ]

        # Get replies recursively
        replies = await self.repository.get_replies(comment.id)
        reply_responses = [
            await self._comment_to_response(reply, current_user_id) for reply in replies
        ]

        # Build author object
        author = comment.author
        author_obj = None
        if author:
            author_obj = {
                "id": author.id,
                "username": author.username,
                "email": author.email,
            }

        return CommentResponse(
            id=comment.id,
            author_id=comment.author_id,
            author=author_obj,
            post_id=comment.post_id,
            title=comment.title,
            description=comment.description,
            parent_comment_id=comment.parent_comment_id,
            mentioned_users=mentioned_users,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            likes_count=likes_count,
            user_has_liked=user_has_liked,
            replies=reply_responses,
        )

    async def _process_mentions(
        self, post_id: int, comment_id: int, content: str, author_id: int
    ) -> None:
        """
        Process mentions in comment content.

        Extracts usernames, validates them, stores mentions, and sends notifications.
        """
        # Extract unique mentions from content
        usernames = extract_mentions(content)

        if not usernames:
            return

        # Get valid users from usernames
        from app.config.database import AsyncSessionLocal
        from app.users.repository import UserRepository

        async with AsyncSessionLocal() as session:
            user_repo = UserRepository(session)
            users = await user_repo.get_by_usernames(usernames)

            # Get actor user for username
            actor = await user_repo.get_by_id(author_id)
            actor_username = actor.username if actor else None

            # Filter out the author (don't mention yourself)
            valid_users = [user for user in users if user.id != author_id]

            if valid_users:
                # Add mentions to comment
                user_ids = [user.id for user in valid_users]
                await self.repository.add_mentions_to_comment(
                    post_id, comment_id, user_ids
                )

                # Send notifications for each mentioned user
                if event_bus_module.event_bus and actor_username:
                    for user in valid_users:
                        await event_bus_module.event_bus.publish(
                            "comment.user_mentioned",
                            {
                                "post_id": post_id,
                                "comment_id": comment_id,
                                "mentioned_user_id": user.id,
                                "mentioned_username": user.username,
                                "actor_id": author_id,
                                "actor_username": actor_username,
                            },
                        )
