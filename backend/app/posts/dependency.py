# app/posts/dependency.py
from app.config.database import get_session
from app.posts.repository import PostRepository
from app.posts.service import PostService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_post_service(session: AsyncSession = Depends(get_session)) -> PostService:
    """Get post service dependency."""
    repository = PostRepository(session)
    return PostService(repository)
