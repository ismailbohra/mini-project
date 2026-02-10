# app/posts/repository.py
from typing import List, Optional

from app.posts.interface import PostRepositoryInterface
from app.posts.model import Posts, PostTag, Tags
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class PostRepository(PostRepositoryInterface):
    """Repository for post database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(
        self, author_id: int, title: str, description: str
    ) -> Posts:
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
            .options(selectinload(Posts.tags).selectinload(PostTag.tag))
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
            .options(selectinload(Posts.tags).selectinload(PostTag.tag))
            .offset(skip)
            .limit(limit)
            .order_by(Posts.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_all_posts(self, skip: int = 0, limit: int = 100) -> List[Posts]:
        """Get all posts."""
        query = (
            select(Posts)
            .where(Posts.is_deleted.is_not(True))
            .options(selectinload(Posts.tags).selectinload(PostTag.tag))
            .offset(skip)
            .limit(limit)
            .order_by(Posts.created_at.desc())
        )
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
