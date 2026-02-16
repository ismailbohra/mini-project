# app/comments/repository.py
from typing import List, Optional

from app.comments.interface import CommentRepositoryInterface
from app.comments.model import Comment, CommentLike, CommentMention, CommentReport
from app.posts.model import ReportStatus
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


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
        # Re-query to eagerly load relationships (author)
        query = (
            select(Comment)
            .where(Comment.id == comment.id)
            .options(selectinload(Comment.author))
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        """Get comment by ID."""
        query = (
            select(Comment)
            .where(Comment.id == comment_id, Comment.is_deleted.is_not(True))
            .options(selectinload(Comment.author))
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
            .options(selectinload(Comment.author))
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
            .options(selectinload(Comment.author))
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
        # Re-query to return the comment with author relationship loaded
        query = (
            select(Comment)
            .where(Comment.id == comment.id)
            .options(selectinload(Comment.author))
        )
        result = await self.session.execute(query)
        return result.scalar_one()

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

    async def create_comment_report(
        self, user_id: int, comment_id: int, reason: str
    ) -> CommentReport:
        """Create a comment report."""
        report = CommentReport(user_id=user_id, comment_id=comment_id, reason=reason)
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_comment_report(
        self, user_id: int, comment_id: int
    ) -> Optional[CommentReport]:
        """Get a specific comment report by user and comment."""
        query = select(CommentReport).where(
            CommentReport.user_id == user_id, CommentReport.comment_id == comment_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_comment_reports(
        self, skip: int = 0, limit: int = 100
    ) -> List[CommentReport]:
        """Get all comment reports (all statuses) with related comment and user data."""
        query = (
            select(CommentReport)
            .options(
                selectinload(CommentReport.comment).selectinload(Comment.author),
                selectinload(CommentReport.user),
            )
            .offset(skip)
            .limit(limit)
            .order_by(CommentReport.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_report_status(
        self, report: CommentReport, status: str
    ) -> CommentReport:
        """Update report status."""
        from datetime import datetime

        report.status = ReportStatus[status.upper()]
        if status.upper() in ["REVIEWED", "DELETED"]:
            report.reviewed_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def add_mentions_to_comment(
        self, post_id: int, comment_id: int, user_ids: List[int]
    ) -> None:
        """Add mentions to a comment."""
        for user_id in user_ids:
            # Check if mention already exists
            existing = await self.session.execute(
                select(CommentMention).where(
                    CommentMention.comment_id == comment_id,
                    CommentMention.user_id == user_id,
                )
            )
            if not existing.scalar_one_or_none():
                mention = CommentMention(
                    post_id=post_id, comment_id=comment_id, user_id=user_id
                )
                self.session.add(mention)
        await self.session.commit()

    async def remove_mentions_from_comment(self, comment_id: int) -> None:
        """Remove all mentions from a comment."""
        await self.session.execute(
            delete(CommentMention).where(CommentMention.comment_id == comment_id)
        )
        await self.session.commit()

    async def get_comment_mentions(self, comment_id: int) -> List[CommentMention]:
        """Get all mentions for a comment."""
        query = (
            select(CommentMention)
            .where(CommentMention.comment_id == comment_id)
            .options(selectinload(CommentMention.user))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
