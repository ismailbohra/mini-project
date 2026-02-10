from typing import List, Optional

from app.auth.model import RoleType
from app.users.model import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AdminRepository:
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
