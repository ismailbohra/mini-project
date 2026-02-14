from typing import Optional

from app.auth.interface import AuthRepositoryInterface
from app.users.model import RoleType, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AuthRepository(AuthRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        username: str,
        email: str,
        hashed_password: str,
        role: RoleType = RoleType.USER,
    ) -> User:
        """Create a new user with default USER role."""
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active=True,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user_password(self, user: User, hashed_password: str) -> User:
        """Update user password."""
        user.hashed_password = hashed_password
        await self.session.commit()
        await self.session.refresh(user)
        return user
