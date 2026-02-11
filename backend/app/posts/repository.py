# app/posts/repository.py
from typing import List, Optional

from app.posts.interface import PostRepositoryInterface
from app.posts.model import PostLike, PostReport, Posts, PostTag, ReportStatus, Tags
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class PostRepository(PostRepositoryInterface):
    """Repository for post database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(self, author_id: int, title: str, description: str) -> Posts:
        """Create a new post."""
        post = Posts(author_id=author_id, title=title, description=description)
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def get_post_by_id(self, post_id: int) -> Optional[Posts]:
        """Get post by ID with tags loaded."""
        query = (
            select(Posts)
            .where(Posts.id == post_id, Posts.is_deleted.is_not(True))
            .options(
                selectinload(Posts.tags).selectinload(PostTag.tag),
                selectinload(Posts.author),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_posts_by_author(
        self, author_id: int, skip: int = 0, limit: int = 100
    ) -> List[Posts]:
        """Get all posts by author."""
        query = (
            select(Posts)
            .where(Posts.author_id == author_id, Posts.is_deleted.is_not(True))
            .options(
                selectinload(Posts.tags).selectinload(PostTag.tag),
                selectinload(Posts.author),
            )
            .offset(skip)
            .limit(limit)
            .order_by(Posts.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_all_posts(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Posts]:
        """Get all posts with search, filter, and sort."""
        from app.users.model import User

        query = (
            select(Posts)
            .where(Posts.is_deleted.is_not(True))
            .options(
                selectinload(Posts.tags).selectinload(PostTag.tag),
                selectinload(Posts.author),
            )
            .distinct()
        )

        # Search functionality
        if search:
            search_term = f"%{search.lower()}%"
            query = (
                query.outerjoin(Posts.author)
                .outerjoin(Posts.tags)
                .outerjoin(PostTag.tag)
            )
            query = query.where(
                func.lower(Posts.title).like(search_term)
                | func.lower(Posts.description).like(search_term)
                | func.lower(User.username).like(search_term)
                | func.lower(Tags.name).like(search_term)
            )

        # Filter by tags
        if tags and len(tags) > 0:
            query = query.join(Posts.tags).join(PostTag.tag)
            query = query.where(Tags.name.in_(tags))

        # Sort
        if sort_order.lower() == "asc":
            query = query.order_by(getattr(Posts, sort_by).asc())
        else:
            query = query.order_by(getattr(Posts, sort_by).desc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_post(
        self,
        post: Posts,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Posts:
        """Update post."""
        if title is not None:
            post.title = title
        if description is not None:
            post.description = description

        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def delete_post(self, post: Posts) -> None:
        """Soft delete post."""
        post.is_deleted = True
        await self.session.commit()

    async def get_or_create_tag(self, tag_name: str) -> Tags:
        """Get existing tag or create new one (case-insensitive)."""
        # Normalize tag name to uppercase for comparison
        normalized_name = tag_name.strip()

        # Try to find existing tag (case-insensitive)
        query = select(Tags).where(Tags.name.ilike(normalized_name))
        result = await self.session.execute(query)
        existing_tag = result.scalar_one_or_none()

        if existing_tag:
            return existing_tag

        # Create new tag with original casing
        new_tag = Tags(name=normalized_name)
        self.session.add(new_tag)
        await self.session.commit()
        await self.session.refresh(new_tag)
        return new_tag

    async def add_tags_to_post(self, post: Posts, tags: List[Tags]) -> None:
        """Add tags to post."""
        for tag in tags:
            post_tag = PostTag(post_id=post.id, tag_id=tag.id)
            self.session.add(post_tag)
        await self.session.commit()

    async def remove_tags_from_post(self, post: Posts) -> None:
        """Remove all tags from post."""
        query = select(PostTag).where(PostTag.post_id == post.id)
        result = await self.session.execute(query)
        post_tags = result.scalars().all()

        for post_tag in post_tags:
            await self.session.delete(post_tag)
        await self.session.commit()

    async def get_post_tags(self, post: Posts) -> List[Tags]:
        """Get all tags for a post."""
        query = (
            select(Tags)
            .join(PostTag)
            .where(PostTag.post_id == post.id)
            .order_by(Tags.name)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_post_like(self, user_id: int, post_id: int) -> PostLike:
        """Add a like to a post."""
        post_like = PostLike(user_id=user_id, post_id=post_id)
        self.session.add(post_like)
        await self.session.commit()
        await self.session.refresh(post_like)
        return post_like

    async def remove_post_like(self, user_id: int, post_id: int) -> None:
        """Remove a like from a post."""
        query = delete(PostLike).where(
            PostLike.user_id == user_id, PostLike.post_id == post_id
        )
        await self.session.execute(query)
        await self.session.commit()

    async def get_post_like(self, user_id: int, post_id: int) -> Optional[PostLike]:
        """Get a specific post like."""
        query = select(PostLike).where(
            PostLike.user_id == user_id, PostLike.post_id == post_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_post_likes_count(self, post_id: int) -> int:
        """Get count of likes for a post."""
        query = (
            select(func.count())
            .select_from(PostLike)
            .where(PostLike.post_id == post_id)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_post_comments_count(self, post_id: int) -> int:
        """Get count of comments for a post."""
        from app.comments.model import Comment

        query = (
            select(func.count())
            .select_from(Comment)
            .where(
                Comment.post_id == post_id,
                Comment.is_deleted.is_not(True),
                Comment.parent_comment_id.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def create_post_report(
        self, user_id: int, post_id: int, reason: str
    ) -> PostReport:
        """Create a post report."""
        report = PostReport(user_id=user_id, post_id=post_id, reason=reason)
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_post_report(self, user_id: int, post_id: int) -> Optional[PostReport]:
        """Get a specific post report by user and post."""
        query = select(PostReport).where(
            PostReport.user_id == user_id, PostReport.post_id == post_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_post_reports(
        self, skip: int = 0, limit: int = 100
    ) -> List[PostReport]:
        """Get all post reports (all statuses) with related post and user data."""
        query = (
            select(PostReport)
            .options(selectinload(PostReport.post), selectinload(PostReport.user))
            .offset(skip)
            .limit(limit)
            .order_by(PostReport.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_report_status(self, report: PostReport, status: str) -> PostReport:
        """Update report status."""
        from datetime import datetime

        report.status = ReportStatus[status.upper()]
        if status.upper() in ["REVIEWED", "DISMISSED"]:
            report.reviewed_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_all_tags(self) -> List[Tags]:
        """Get all tags."""
        query = select(Tags).order_by(Tags.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search_suggestions(self, search: str, limit: int = 10) -> List[dict]:
        """Get search suggestions based on partial match."""
        from app.users.model import User

        search_term = f"%{search.lower()}%"
        suggestions = []

        # Search in post titles
        title_query = (
            select(Posts.title)
            .where(
                Posts.is_deleted.is_not(True),
                func.lower(Posts.title).like(search_term),
            )
            .distinct()
            .limit(limit)
        )
        title_results = await self.session.execute(title_query)
        for title in title_results.scalars().all():
            suggestions.append({"type": "title", "value": title})

        # Search in author names
        author_query = (
            select(User.username)
            .join(Posts, User.id == Posts.author_id)
            .where(
                Posts.is_deleted.is_not(True),
                func.lower(User.username).like(search_term),
            )
            .distinct()
            .limit(limit)
        )
        author_results = await self.session.execute(author_query)
        for username in author_results.scalars().all():
            suggestions.append({"type": "author", "value": username})

        # Search in tag names
        tag_query = (
            select(Tags.name)
            .where(func.lower(Tags.name).like(search_term))
            .distinct()
            .limit(limit)
        )
        tag_results = await self.session.execute(tag_query)
        for tag_name in tag_results.scalars().all():
            suggestions.append({"type": "tag", "value": tag_name})

        return suggestions[:limit]
