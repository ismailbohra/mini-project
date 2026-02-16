from typing import List, Optional, Tuple

from app.admin.interface import AdminRepositoryInterface
from app.posts.model import PostMention, PostReport, Posts, PostTag, Tags
from app.users.model import RoleType, User
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class AdminRepository(AdminRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users."""
        query = select(User).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_user_role(self, user: User, role: RoleType) -> User:
        """Update user role."""
        user.role = role
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def toggle_user(self, user: User) -> User:
        """Toggle a user's active status (activate/deactivate)."""
        # Flip the active flag
        user.is_active = not user.is_active
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_stats_by_role(self) -> Tuple[int, int, int, int]:
        """Get user statistics by role (total, admin, moderator, normal)."""
        # Total users
        total_query = select(func.count(User.id)).where(User.is_deleted == False)
        total_result = await self.session.execute(total_query)
        total_users = total_result.scalar() or 0

        # Admin count
        admin_query = select(func.count(User.id)).where(
            User.role == RoleType.ADMIN, User.is_deleted == False
        )
        admin_result = await self.session.execute(admin_query)
        admin_count = admin_result.scalar() or 0

        # Moderator count
        moderator_query = select(func.count(User.id)).where(
            User.role == RoleType.MODERATOR, User.is_deleted == False
        )
        moderator_result = await self.session.execute(moderator_query)
        moderator_count = moderator_result.scalar() or 0

        # Normal user count
        user_query = select(func.count(User.id)).where(
            User.role == RoleType.USER, User.is_deleted == False
        )
        user_result = await self.session.execute(user_query)
        normal_user_count = user_result.scalar() or 0

        return total_users, admin_count, moderator_count, normal_user_count

    async def get_total_posts(self) -> int:
        """Get total number of posts."""
        query = select(func.count(Posts.id)).where(Posts.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_user_with_most_posts(self) -> Optional[Tuple[int, str, str, int]]:
        """Get user with most posts (user_id, username, profile_image, post_count)."""
        query = (
            select(
                User.id,
                User.username,
                User.profile_image,
                func.count(Posts.id).label("post_count"),
            )
            .join(Posts, User.id == Posts.author_id)
            .where(Posts.is_deleted == False, User.is_deleted == False)
            .group_by(User.id, User.username, User.profile_image)
            .order_by(func.count(Posts.id).desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        row = result.first()
        return row if row else None

    async def get_top_mentioned_users(
        self, limit: int = 5
    ) -> List[Tuple[int, str, str, int]]:
        """Get top mentioned users (user_id, username, profile_image, mention_count)."""
        query = (
            select(
                User.id,
                User.username,
                User.profile_image,
                func.count(PostMention.user_id).label("mention_count"),
            )
            .join(PostMention, User.id == PostMention.user_id)
            .where(User.is_deleted == False)
            .group_by(User.id, User.username, User.profile_image)
            .order_by(func.count(PostMention.user_id).desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.all())

    async def get_top_tags(self, limit: int = 5) -> List[Tuple[int, str, int]]:
        """Get top tags (tag_id, tag_name, usage_count)."""
        query = (
            select(
                Tags.id,
                Tags.name,
                func.count(PostTag.tag_id).label("usage_count"),
            )
            .join(PostTag, Tags.id == PostTag.tag_id)
            .group_by(Tags.id, Tags.name)
            .order_by(func.count(PostTag.tag_id).desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.all())

    async def get_top_reported_users(
        self, limit: int = 5
    ) -> List[Tuple[int, str, str, int]]:
        """Get users whose posts got reported most (user_id, username, profile_image, report_count)."""
        query = (
            select(
                User.id,
                User.username,
                User.profile_image,
                func.count(PostReport.id).label("report_count"),
            )
            .join(Posts, User.id == Posts.author_id)
            .join(PostReport, Posts.id == PostReport.post_id)
            .where(User.is_deleted == False, Posts.is_deleted == False)
            .group_by(User.id, User.username, User.profile_image)
            .order_by(func.count(PostReport.id).desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.all())
