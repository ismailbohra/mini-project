# app/moderator/service.py
from typing import List

from app.comments.interface import CommentRepositoryInterface
from app.comments.model import Comment
from app.comments.schema import CommentReportResponse, CommentResponse, CommentUpdate
from app.posts.interface import PostRepositoryInterface
from app.posts.schema import PostReportResponse, PostResponse, PostUpdate
from app.utils.exceptions import NotFoundException


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
        """Get all pending post reports."""
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
            )
            for report in reports
        ]

    async def update_post_report_status(
        self, report_id: int, status: str
    ) -> PostReportResponse:
        """Update post report status."""
        # Get all reports to find by id
        reports = await self.post_repository.get_pending_post_reports(skip=0, limit=1000)
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
        )

    # Comment Report Management
    async def get_pending_comment_reports(
        self, skip: int = 0, limit: int = 100
    ) -> List[CommentReportResponse]:
        """Get all pending comment reports."""
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
        )

    # Post Management
    async def get_all_posts(
        self, skip: int = 0, limit: int = 100
    ) -> List[PostResponse]:
        """Get all posts."""
        from app.posts.schema import TagResponse

        posts = await self.post_repository.get_all_posts(skip, limit)
        return [
            PostResponse(
                id=post.id,
                author_id=post.author_id,
                title=post.title,
                description=post.description,
                tags=[
                    TagResponse(id=pt.tag.id, name=pt.tag.name) for pt in post.tags
                ],
                created_at=post.created_at,
                updated_at=post.updated_at,
            )
            for post in posts
        ]

    async def update_any_post(
        self, post_id: int, post_data: PostUpdate
    ) -> PostResponse:
        """Update any post (moderator privilege)."""
        from app.posts.schema import TagResponse

        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with id {post_id} not found")

        # Update post fields
        post = await self.post_repository.update_post(
            post, title=post_data.title, description=post_data.description
        )

        # Update tags if provided
        if post_data.tags is not None:
            await self.post_repository.remove_tags_from_post(post)
            if post_data.tags:
                tags = []
                for tag_name in post_data.tags:
                    tag = await self.post_repository.get_or_create_tag(tag_name)
                    tags.append(tag)
                await self.post_repository.add_tags_to_post(post, tags)

        # Fetch updated post
        updated_post = await self.post_repository.get_post_by_id(post_id)
        return PostResponse(
            id=updated_post.id,
            author_id=updated_post.author_id,
            title=updated_post.title,
            description=updated_post.description,
            tags=[TagResponse(id=pt.tag.id, name=pt.tag.name) for pt in updated_post.tags],
            created_at=updated_post.created_at,
            updated_at=updated_post.updated_at,
        )

    async def delete_any_post(self, post_id: int) -> None:
        """Delete any post (moderator privilege)."""
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with id {post_id} not found")
        await self.post_repository.delete_post(post)

    # Comment Management
    async def update_any_comment(
        self, comment_id: int, comment_data: CommentUpdate
    ) -> CommentResponse:
        """Update any comment (moderator privilege)."""
        comment = await self.comment_repository.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment with id {comment_id} not found")

        comment = await self.comment_repository.update_comment(
            comment, title=comment_data.title, description=comment_data.description
        )

        return await self._comment_to_response(comment)

    async def delete_any_comment(self, comment_id: int) -> None:
        """Delete any comment (moderator privilege)."""
        comment = await self.comment_repository.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Comment with id {comment_id} not found")
        await self.comment_repository.delete_comment(comment)

    async def _comment_to_response(self, comment: Comment) -> CommentResponse:
        """Convert Comment model to CommentResponse."""
        likes_count = await self.comment_repository.get_comment_likes_count(comment.id)
        replies = await self.comment_repository.get_replies(comment.id)
        reply_responses = [await self._comment_to_response(reply) for reply in replies]

        return CommentResponse(
            id=comment.id,
            author_id=comment.author_id,
            post_id=comment.post_id,
            title=comment.title,
            description=comment.description,
            parent_comment_id=comment.parent_comment_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            likes_count=likes_count,
            replies=reply_responses,
        )
