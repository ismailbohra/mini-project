# app/moderator/dependency.py
from app.comments.repository import CommentRepository
from app.config.database import get_session
from app.moderator.service import ModeratorService
from app.posts.repository import PostRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_moderator_service(
    session: AsyncSession = Depends(get_session),
) -> ModeratorService:
    """Get moderator service dependency."""
    post_repository = PostRepository(session)
    comment_repository = CommentRepository(session)
    return ModeratorService(post_repository, comment_repository)
