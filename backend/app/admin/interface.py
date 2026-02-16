# app/admin/interface.py
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.users.model import RoleType, User


class AdminRepositoryInterface(ABC):
    """Interface for admin repository."""

    @abstractmethod
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users."""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def update_user_role(self, user: User, role: RoleType) -> User:
        """Update user role."""
        pass

    @abstractmethod
    async def toggle_user(self, user: User) -> User:
        """Toggle a user's active status (activate/deactivate)."""
        pass

    @abstractmethod
    async def get_user_stats_by_role(self) -> Tuple[int, int, int, int]:
        """Get user statistics by role (total, admin, moderator, normal)."""
        pass

    @abstractmethod
    async def get_total_posts(self) -> int:
        """Get total number of posts."""
        pass

    @abstractmethod
    async def get_user_with_most_posts(self) -> Optional[Tuple[int, str, str, int]]:
        """Get user with most posts (user_id, username, profile_image, post_count)."""
        pass

    @abstractmethod
    async def get_top_mentioned_users(
        self, limit: int = 5
    ) -> List[Tuple[int, str, str, int]]:
        """Get top mentioned users (user_id, username, profile_image, mention_count)."""
        pass

    @abstractmethod
    async def get_top_tags(self, limit: int = 5) -> List[Tuple[int, str, int]]:
        """Get top tags (tag_id, tag_name, usage_count)."""
        pass

    @abstractmethod
    async def get_top_reported_users(
        self, limit: int = 5
    ) -> List[Tuple[int, str, str, int]]:
        """Get users whose posts got reported most (user_id, username, profile_image, report_count)."""
        pass
