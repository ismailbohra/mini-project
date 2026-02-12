# app/moderator/service.py
from typing import List

from app.comments.interface import CommentRepositoryInterface
from app.comments.schema import CommentReportResponse
from app.posts.interface import PostRepositoryInterface
from app.posts.schema import PostReportResponse
from app.utils.exceptions import NotFoundException
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ModeratorService:
    """Service for moderator actions."""

    def __init__(
        self,
        post_repository: PostRepositoryInterface,
        comment_repository: CommentRepositoryInterface,
    ):
        self.post_repository = post_repository
        self.comment_repository = comment_repository

    # Post Report Management
    async def get_pending_post_reports(
        self, skip: int = 0, limit: int = 100
    ) -> List[PostReportResponse]:
        """Get all post reports with enriched data."""
        reports = await self.post_repository.get_pending_post_reports(skip, limit)
        return [
            PostReportResponse(
                id=report.id,
                user_id=report.user_id,
                post_id=report.post_id,
                reason=report.reason,
                status=report.status.value,
                created_at=report.created_at,
                reviewed_at=report.reviewed_at,
                # Enriched fields
                post_title=report.post.title if report.post else None,
                post_author_id=report.post.author_id if report.post else None,
                reporter_username=report.user.username if report.user else None,
            )
            for report in reports
        ]

    async def update_post_report_status(
        self, report_id: int, status: str
    ) -> PostReportResponse:
        """Update post report status."""
        # Get all reports to find by id
        reports = await self.post_repository.get_pending_post_reports(
            skip=0, limit=1000
        )
        report = next((r for r in reports if r.id == report_id), None)

        if not report:
            raise NotFoundException(f"Report with id {report_id} not found")

        updated_report = await self.post_repository.update_report_status(report, status)
        return PostReportResponse(
            id=updated_report.id,
            user_id=updated_report.user_id,
            post_id=updated_report.post_id,
            reason=updated_report.reason,
            status=updated_report.status.value,
            created_at=updated_report.created_at,
            reviewed_at=updated_report.reviewed_at,
            # Enriched fields
            post_title=updated_report.post.title if updated_report.post else None,
            post_author_id=updated_report.post.author_id
            if updated_report.post
            else None,
            reporter_username=updated_report.user.username
            if updated_report.user
            else None,
        )

    # Comment Report Management
    async def get_pending_comment_reports(
        self, skip: int = 0, limit: int = 100
    ) -> List[CommentReportResponse]:
        """Get all comment reports with enriched data."""
        reports = await self.comment_repository.get_pending_comment_reports(skip, limit)
        return [
            CommentReportResponse(
                id=report.id,
                user_id=report.user_id,
                comment_id=report.comment_id,
                reason=report.reason,
                status=report.status.value,
                created_at=report.created_at,
                reviewed_at=report.reviewed_at,
                # Enriched fields
                comment_title=report.comment.title if report.comment else None,
                comment_description=report.comment.description
                if report.comment
                else None,
                comment_author_id=report.comment.author_id if report.comment else None,
                comment_author_username=report.comment.author.username
                if report.comment and report.comment.author
                else None,
                reporter_username=report.user.username if report.user else None,
            )
            for report in reports
        ]

    async def update_comment_report_status(
        self, report_id: int, status: str
    ) -> CommentReportResponse:
        """Update comment report status."""
        # Get all reports to find by id
        reports = await self.comment_repository.get_pending_comment_reports(
            skip=0, limit=1000
        )
        report = next((r for r in reports if r.id == report_id), None)

        if not report:
            raise NotFoundException(f"Report with id {report_id} not found")

        updated_report = await self.comment_repository.update_report_status(
            report, status
        )
        return CommentReportResponse(
            id=updated_report.id,
            user_id=updated_report.user_id,
            comment_id=updated_report.comment_id,
            reason=updated_report.reason,
            status=updated_report.status.value,
            created_at=updated_report.created_at,
            reviewed_at=updated_report.reviewed_at,
            # Enriched fields
            comment_title=updated_report.comment.title
            if updated_report.comment
            else None,
            comment_description=updated_report.comment.description
            if updated_report.comment
            else None,
            comment_author_id=updated_report.comment.author_id
            if updated_report.comment
            else None,
            comment_author_username=updated_report.comment.author.username
            if updated_report.comment and updated_report.comment.author
            else None,
            reporter_username=updated_report.user.username
            if updated_report.user
            else None,
        )
