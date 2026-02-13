from typing import List, Optional

from app.users.interface import UserRepositoryInterface
from app.users.model import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(UserRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        query = select(User).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, update_data: dict) -> User:
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def search_by_username(self, search_term: str, limit: int = 10) -> List[User]:
        """Search users by username pattern for mention autocomplete."""
        query = (
            select(User)
            .where(User.username.ilike(f"%{search_term}%"))
            .where(User.is_active == True)
            .where(User.is_deleted == False)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_usernames(self, usernames: List[str]) -> List[User]:
        """Get users by a list of usernames."""
        # Use case-insensitive comparison
        query = (
            select(User)
            .where(User.username.in_(usernames))
            .where(User.is_active == True)
            .where(User.is_deleted == False)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
