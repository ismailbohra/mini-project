from typing import List

from app.admin.dependency import get_admin_service
from app.admin.schema import (
    AssignRoleRequest,
    AssignRoleResponse,
    DashboardAnalyticsResponse,
    ToggleUserResponse,
)
from app.admin.service import AdminService
from app.auth.dependency import get_current_user_id, require_admin
from app.users.schema import UserResponse
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/assign-role",
    response_model=AssignRoleResponse,
    summary="Assign role to user (Admin only)",
    description="Admin can assign roles (Admin, User, Moderator) to any user",
)
async def assign_role(
    request: AssignRoleRequest,
    user_id: int = Depends(get_current_user_id),
    admin_service: AdminService = Depends(get_admin_service),
    _: bool = Depends(require_admin),
) -> AssignRoleResponse:
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


@router.patch(
    "/users/{user_id}/toggle",
    response_model=ToggleUserResponse,
    summary="Toggle user's active status (Admin only)",
    description="Admin can activate or deactivate any user by their ID",
)
async def toggle_user(
    user_id: int,
    admin_service: AdminService = Depends(get_admin_service),
    _: bool = Depends(require_admin),
) -> ToggleUserResponse:
    """
    Toggle a user's active status (Admin only)
    - **user_id**: ID of the user to toggle (activate/deactivate)

    Requires Admin role.
    """
    return await admin_service.toggle_user(user_id)


@router.get(
    "/dashboard/analytics",
    response_model=DashboardAnalyticsResponse,
    summary="Get dashboard analytics (Admin only)",
    description="Retrieve comprehensive analytics for admin dashboard including user stats, post stats, mentions, tags, and reports",
)
async def get_dashboard_analytics(
    admin_service: AdminService = Depends(get_admin_service),
    _: bool = Depends(require_admin),
) -> DashboardAnalyticsResponse:
    """
    Get comprehensive dashboard analytics (Admin only):
    - **User Statistics**: Total users, admin count, moderator count, normal user count, active users
    - **Post Statistics**: Total posts, user with most posts
    - **Engagement**: Top 5 mentioned users, top 5 tags
    - **Moderation**: Top 5 reported users

    Requires Admin role.
    """
    return await admin_service.get_dashboard_analytics()


@router.websocket("/dashboard/ws")
async def admin_dashboard_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time admin dashboard updates.
    Sends active user count updates in real-time.
    """
    from app.websocket.manager import ws_manager

    await websocket.accept()

    try:
        # Receive initial connection data with user_id
        data = await websocket.receive_json()
        user_id = data.get("user_id")

        if not user_id:
            await websocket.close(code=1008)
            return

        # Connect to admin dashboard
        await ws_manager.connect_admin_dashboard(user_id, websocket)

        try:
            # Keep connection alive and listen for client messages
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await ws_manager.disconnect_admin_dashboard(user_id, websocket)
    except Exception:
        if user_id:
            await ws_manager.disconnect_admin_dashboard(user_id, websocket)
        await websocket.close()
