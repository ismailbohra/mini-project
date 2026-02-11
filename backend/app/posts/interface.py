# app/posts/interface.py
from abc import ABC, abstractmethod
from typing import List, Optional

from app.posts.model import PostLike, PostReport, Posts, Tags


class PostRepositoryInterface(ABC):
    """Interface for post repository."""

    @abstractmethod
    async def create_post(self, author_id: int, title: str, description: str) -> Posts:
        """Create a new post."""
        pass

    @abstractmethod
    async def get_post_by_id(self, post_id: int) -> Optional[Posts]:
        """Get post by ID."""
        pass

    @abstractmethod
    async def get_posts_by_author(
        self, author_id: int, skip: int = 0, limit: int = 100
    ) -> List[Posts]:
        """Get all posts by author."""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def update_post(
        self,
        post: Posts,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Posts:
        """Update post."""
        pass

    @abstractmethod
    async def delete_post(self, post: Posts) -> None:
        """Soft delete post."""
        pass

    @abstractmethod
    async def get_or_create_tag(self, tag_name: str) -> Tags:
        """Get existing tag or create new one (case-insensitive)."""
        pass

    @abstractmethod
    async def add_tags_to_post(self, post: Posts, tags: List[Tags]) -> None:
        """Add tags to post."""
        pass

    @abstractmethod
    async def remove_tags_from_post(self, post: Posts) -> None:
        """Remove all tags from post."""
        pass

    @abstractmethod
    async def get_post_tags(self, post: Posts) -> List[Tags]:
        """Get all tags for a post."""
        pass

    @abstractmethod
    async def add_post_like(self, user_id: int, post_id: int) -> PostLike:
        """Add a like to a post."""
        pass

    @abstractmethod
    async def remove_post_like(self, user_id: int, post_id: int) -> None:
        """Remove a like from a post."""
        pass

    @abstractmethod
    async def get_post_like(self, user_id: int, post_id: int) -> Optional[PostLike]:
        """Get a specific post like."""
        pass

    @abstractmethod
    async def get_post_likes_count(self, post_id: int) -> int:
        """Get count of likes for a post."""
        pass

    @abstractmethod
    async def get_post_comments_count(self, post_id: int) -> int:
        """Get count of comments for a post."""
        pass

    @abstractmethod
    async def create_post_report(
        self, user_id: int, post_id: int, reason: str
    ) -> PostReport:
        """Create a post report."""
        pass

    @abstractmethod
    async def get_post_report(self, user_id: int, post_id: int) -> Optional[PostReport]:
        """Get a specific post report by user and post."""
        pass

    @abstractmethod
    async def get_pending_post_reports(
        self, skip: int = 0, limit: int = 100
    ) -> List[PostReport]:
        """Get all pending post reports."""
        pass

    @abstractmethod
    async def update_report_status(self, report: PostReport, status: str) -> PostReport:
        """Update report status."""
        pass

    @abstractmethod
    async def get_all_tags(self) -> List[Tags]:
        pass

    @abstractmethod
    async def search_suggestions(self, search: str, limit: int = 10) -> List[dict]:
        """Get search suggestions based on partial match."""
        pass
