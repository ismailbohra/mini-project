# app/comments/interface.py
from abc import ABC, abstractmethod
from typing import List, Optional

from app.comments.model import Comment, CommentLike


class CommentRepositoryInterface(ABC):
    """Interface for comment repository."""

    @abstractmethod
    async def create_comment(
        self,
        author_id: int,
        post_id: int,
        title: str,
        description: str,
        parent_comment_id: Optional[int] = None,
    ) -> Comment:
        """Create a new comment."""
        pass

    @abstractmethod
    async def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        """Get comment by ID."""
        pass

    @abstractmethod
    async def get_comments_by_post(
        self, post_id: int, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get all comments for a post (top-level only)."""
        pass

    @abstractmethod
    async def get_replies(self, parent_comment_id: int) -> List[Comment]:
        """Get all replies to a comment."""
        pass

    @abstractmethod
    async def update_comment(
        self,
        comment: Comment,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Comment:
        """Update comment."""
        pass

    @abstractmethod
    async def delete_comment(self, comment: Comment) -> None:
        """Soft delete comment."""
        pass

    @abstractmethod
    async def get_comment_likes_count(self, comment_id: int) -> int:
        """Get count of likes for a comment."""
        pass

    @abstractmethod
    async def add_comment_like(self, user_id: int, comment_id: int) -> CommentLike:
        """Add a like to a comment."""
        pass

    @abstractmethod
    async def remove_comment_like(self, user_id: int, comment_id: int) -> None:
        """Remove a like from a comment."""
        pass

    @abstractmethod
    async def get_comment_like(
        self, user_id: int, comment_id: int
    ) -> Optional[CommentLike]:
        """Get a specific comment like."""
        pass
