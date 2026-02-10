from typing import List

from app.admin.dependency import get_admin_service
from app.admin.schema import AssignRoleRequest
from app.admin.service import AdminService
from app.auth.dependency import get_current_user_id, require_admin
from app.users.schema import UserResponse
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/assign-role",
    response_model=UserResponse,
    summary="Assign role to user (Admin only)",
    description="Admin can assign roles (Admin, User, Moderator) to any user",
)
async def assign_role(
    request: AssignRoleRequest,
    user_id: int = Depends(get_current_user_id),
    admin_service: AdminService = Depends(get_admin_service),
    _: bool = Depends(require_admin),
) -> UserResponse:
    """
    Assign a role to a user (Admin only):
    - **user_id**: Target user's ID
    - **role**: Role to assign (Admin, User, or Moderator)

    Requires Admin role.
    """
    return await admin_service.assign_role(request, assigned_by_id=user_id)


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="Get all users (Admin only)",
    description="Retrieve a list of all users with their roles",
)
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin_service: AdminService = Depends(get_admin_service),
    _: bool = Depends(require_admin),
) -> List[UserResponse]:
    """
    Get all users (Admin only)
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return

    Requires Admin role.
    """
    return await admin_service.get_all_users(skip=skip, limit=limit)
