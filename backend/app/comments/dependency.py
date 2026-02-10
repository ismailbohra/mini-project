# app/comments/dependency.py
from app.comments.repository import CommentRepository
from app.comments.service import CommentService
from app.config.database import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_comment_service(session: AsyncSession = Depends(get_session)) -> CommentService:
    """Get comment service dependency."""
    repository = CommentRepository(session)
    return CommentService(repository)
