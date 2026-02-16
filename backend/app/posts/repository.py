# app/posts/repository.py
from typing import List, Optional

from app.posts.interface import PostRepositoryInterface
from app.posts.model import (
    PostLike,
    PostMention,
    PostReport,
    Posts,
    PostTag,
    ReportStatus,
    Tags,
)
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class PostRepository(PostRepositoryInterface):
    """Repository for post database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(
        self,
        author_id: int,
        title: str,
        description: str,
        image_path: str | None = None,
    ) -> Posts:
        """Create a new post."""
        post = Posts(
            author_id=author_id,
            title=title,
            description=description,
            image_path=image_path,
        )
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
    ) -> tuple[List[Posts], int]:
        """Get all posts by author with total count."""
        # Get total count
        count_query = (
            select(func.count())
            .select_from(Posts)
            .where(Posts.author_id == author_id, Posts.is_deleted.is_not(True))
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Get posts
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
        posts = list(result.scalars().all())

        return posts, total

    async def get_all_posts(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[List[Posts], int]:
        """Get all posts with search, filter, and sort, including total count."""
        from app.users.model import User

        # Build base query for counting
        count_query = (
            select(func.count(Posts.id.distinct()))
            .select_from(Posts)
            .where(Posts.is_deleted.is_not(True))
        )

        # Build base query for fetching posts
        query = (
            select(Posts)
            .where(Posts.is_deleted.is_not(True))
            .options(
                selectinload(Posts.tags).selectinload(PostTag.tag),
                selectinload(Posts.author),
            )
        )

        # Track if we need distinct (when joins are added)
        needs_distinct = False
        has_tag_join = False

        # Search functionality
        if search:
            search_term = f"%{search.lower()}%"
            needs_distinct = True
            has_tag_join = True
            # Apply search to count query
            count_query = (
                count_query.outerjoin(Posts.author)
                .outerjoin(Posts.tags)
                .outerjoin(PostTag.tag)
            )
            count_query = count_query.where(
                func.lower(Posts.title).like(search_term)
                | func.lower(Posts.description).like(search_term)
                | func.lower(User.username).like(search_term)
                | func.lower(Tags.name).like(search_term)
            )
            # Apply search to posts query
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
            needs_distinct = True
            # Only add joins if not already added by search
            if not has_tag_join:
                count_query = count_query.join(Posts.tags).join(PostTag.tag)
                query = query.join(Posts.tags).join(PostTag.tag)
            # Apply tags filter
            count_query = count_query.where(Tags.name.in_(tags))
            query = query.where(Tags.name.in_(tags))

        # Get total count
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Apply distinct if needed (when we have joins that could create duplicates)
        if needs_distinct:
            query = query.distinct()

        # Sort - apply after distinct
        sort_column = getattr(Posts, sort_by)
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        posts = list(result.scalars().all())

        return posts, total

    async def update_post(
        self,
        post: Posts,
        title: Optional[str] = None,
        description: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> Posts:
        """Update post."""
        if title is not None:
            post.title = title
        if description is not None:
            post.description = description
        if image_path is not None:
            post.image_path = image_path

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

        import app.utils.redis as redis_utils

        await redis_utils.delete_cache("tags:all")

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
        if status.upper() in ["REVIEWED", "DELETED"]:
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

    async def add_mentions_to_post(self, post_id: int, user_ids: List[int]) -> None:
        """Add mentions to a post."""
        for user_id in user_ids:
            # Check if mention already exists
            existing = await self.session.execute(
                select(PostMention).where(
                    PostMention.post_id == post_id, PostMention.user_id == user_id
                )
            )
            if not existing.scalar_one_or_none():
                mention = PostMention(post_id=post_id, user_id=user_id)
                self.session.add(mention)
        await self.session.commit()

    async def remove_mentions_from_post(self, post_id: int) -> None:
        """Remove all mentions from a post."""
        await self.session.execute(
            delete(PostMention).where(PostMention.post_id == post_id)
        )
        await self.session.commit()

    async def get_post_mentions(self, post_id: int) -> List[PostMention]:
        """Get all mentions for a post."""
        query = (
            select(PostMention)
            .where(PostMention.post_id == post_id)
            .options(selectinload(PostMention.user))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
