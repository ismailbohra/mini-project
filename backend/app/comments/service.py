# app/comments/service.py
from typing import List, Optional

from app.comments.interface import CommentRepositoryInterface
from app.comments.model import Comment
from app.comments.schema import (
    CommentCreate,
    CommentLikeResponse,
    CommentReportResponse,
    CommentResponse,
    CommentUpdate,
)
from app.utils.exceptions import ForbiddenException, NotFoundException


class CommentService:
    """Service for comment business logic."""

    def __init__(self, repository: CommentRepositoryInterface):
        self.repository = repository

    async def create_comment(
        self, author_id: int, comment_data: CommentCreate, current_user_id: Optional[int] = None
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

        return await self._comment_to_response(comment, current_user_id)

    async def get_comment(self, comment_id: int, current_user_id: Optional[int] = None) -> CommentResponse:
        """Get a comment by ID with nested replies."""
        comment = await self.repository.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment with id {comment_id} not found")
        return await self._comment_to_response(comment, current_user_id)

    async def get_post_comments(
        self, post_id: int, skip: int = 0, limit: int = 100, current_user_id: Optional[int] = None
    ) -> List[CommentResponse]:
        """Get all top-level comments for a post with nested replies."""
        comments = await self.repository.get_comments_by_post(post_id, skip, limit)
        return [await self._comment_to_response(comment, current_user_id) for comment in comments]

    async def update_comment(
        self, comment_id: int, author_id: int, comment_data: CommentUpdate, current_user_id: Optional[int] = None
    ) -> CommentResponse:
        """Update a comment."""
        comment = await self.repository.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment with id {comment_id} not found")

        # Check if user is the author
        if comment.author_id != author_id:
            raise ForbiddenException("You can only update your own comments")

        comment = await self.repository.update_comment(
            comment, title=comment_data.title, description=comment_data.description
        )

        return await self._comment_to_response(comment, current_user_id)

    async def delete_comment(self, comment_id: int, author_id: int) -> None:
        """Delete a comment."""
        comment = await self.repository.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment with id {comment_id} not found")

        # Check if user is the author
        if comment.author_id != author_id:
            raise ForbiddenException("You can only delete your own comments")

        await self.repository.delete_comment(comment)

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

        await self.repository.remove_comment_like(user_id, comment_id)

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

    async def _comment_to_response(self, comment: Comment, current_user_id: Optional[int] = None) -> CommentResponse:
        """Convert Comment model to CommentResponse with nested replies."""
        # Get likes count
        likes_count = await self.repository.get_comment_likes_count(comment.id)

        # Check if current user has liked this comment
        user_has_liked = False
        if current_user_id:
            like = await self.repository.get_comment_like(current_user_id, comment.id)
            user_has_liked = like is not None

        # Get replies recursively
        replies = await self.repository.get_replies(comment.id)
        reply_responses = [await self._comment_to_response(reply, current_user_id) for reply in replies]

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
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            likes_count=likes_count,
            user_has_liked=user_has_liked,
            replies=reply_responses,
        )
