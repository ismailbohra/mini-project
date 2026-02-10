# app/comments/repository.py
from typing import List, Optional

from app.comments.interface import CommentRepositoryInterface
from app.comments.model import Comment, CommentLike
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


class CommentRepository(CommentRepositoryInterface):
    """Repository for comment database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_comment(
        self,
        author_id: int,
        post_id: int,
        title: str,
        description: str,
        parent_comment_id: Optional[int] = None,
    ) -> Comment:
        """Create a new comment."""
        comment = Comment(
            author_id=author_id,
            post_id=post_id,
            title=title,
            description=description,
            parent_comment_id=parent_comment_id,
        )
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        """Get comment by ID."""
        query = select(Comment).where(
            Comment.id == comment_id, Comment.is_deleted.is_not(True)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_comments_by_post(
        self, post_id: int, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get all top-level comments for a post (no parent)."""
        query = (
            select(Comment)
            .where(
                Comment.post_id == post_id,
                Comment.parent_comment_id.is_(None),
                Comment.is_deleted.is_not(True),
            )
            .offset(skip)
            .limit(limit)
            .order_by(Comment.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_replies(self, parent_comment_id: int) -> List[Comment]:
        """Get all replies to a comment."""
        query = (
            select(Comment)
            .where(
                Comment.parent_comment_id == parent_comment_id,
                Comment.is_deleted.is_not(True),
            )
            .order_by(Comment.created_at.asc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_comment(
        self,
        comment: Comment,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Comment:
        """Update comment."""
        if title is not None:
            comment.title = title
        if description is not None:
            comment.description = description

        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def delete_comment(self, comment: Comment) -> None:
        """Soft delete comment."""
        comment.is_deleted = True
        await self.session.commit()

    async def get_comment_likes_count(self, comment_id: int) -> int:
        """Get count of likes for a comment."""
        query = (
            select(func.count())
            .select_from(CommentLike)
            .where(CommentLike.comment_id == comment_id)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def add_comment_like(self, user_id: int, comment_id: int) -> CommentLike:
        """Add a like to a comment."""
        comment_like = CommentLike(user_id=user_id, comment_id=comment_id)
        self.session.add(comment_like)
        await self.session.commit()
        await self.session.refresh(comment_like)
        return comment_like

    async def remove_comment_like(self, user_id: int, comment_id: int) -> None:
        """Remove a like from a comment."""
        query = delete(CommentLike).where(
            CommentLike.user_id == user_id, CommentLike.comment_id == comment_id
        )
        await self.session.execute(query)
        await self.session.commit()

    async def get_comment_like(
        self, user_id: int, comment_id: int
    ) -> Optional[CommentLike]:
        """Get a specific comment like."""
        query = select(CommentLike).where(
            CommentLike.user_id == user_id, CommentLike.comment_id == comment_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
