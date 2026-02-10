from app.config.database import get_session
from app.users.repository import UserRepository
from app.users.service import UserService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    repository = UserRepository(session)
    return UserService(repository)
