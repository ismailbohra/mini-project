from app.admin.repository import AdminRepository
from app.admin.service import AdminService
from app.config.database import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_admin_service(session: AsyncSession = Depends(get_session)) -> AdminService:
    """Get admin service dependency."""
    repository = AdminRepository(session)
    return AdminService(repository)
