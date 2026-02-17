from datetime import datetime
from typing import Optional

from app.auth.interface import AuthRepositoryInterface
from app.auth.model import PasswordResetToken
from app.users.model import RoleType, User
from sqlalchemy import delete, select
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

    async def create_password_reset_token(
        self, user_id: int, token: str, expires_at: datetime
    ) -> PasswordResetToken:
        """Create a password reset token."""
        reset_token = PasswordResetToken(
            user_id=user_id, token=token, expires_at=expires_at, is_used=False
        )
        self.session.add(reset_token)
        await self.session.commit()
        await self.session.refresh(reset_token)
        return reset_token

    async def get_password_reset_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get password reset token by token string."""
        query = select(PasswordResetToken).where(PasswordResetToken.token == token)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def mark_token_as_used(self, token: PasswordResetToken) -> PasswordResetToken:
        """Mark password reset token as used."""
        token.is_used = True
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def delete_user_reset_tokens(self, user_id: int) -> None:
        """Delete all password reset tokens for a user."""
        query = delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
        await self.session.execute(query)
        await self.session.commit()
