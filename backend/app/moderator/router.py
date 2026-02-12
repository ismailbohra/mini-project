# app/moderator/router.py
from typing import List

from app.auth.dependency import require_moderator
from app.comments.schema import CommentReportResponse
from app.moderator.dependency import get_moderator_service
from app.moderator.service import ModeratorService
from app.posts.schema import PostReportResponse
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="/moderator", tags=["moderator"])


# Report Management
@router.get(
    "/reports/posts",
    response_model=List[PostReportResponse],
    summary="Get all post reports",
)
async def get_pending_post_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    _: bool = Depends(require_moderator),
    moderator_service: ModeratorService = Depends(get_moderator_service),
):
    """Get all post reports (pending, reviewed, dismissed). Moderator only."""
    return await moderator_service.get_pending_post_reports(skip, limit)


@router.put(
    "/reports/posts/{report_id}/status",
    response_model=PostReportResponse,
    summary="Update post report status",
)
async def update_post_report_status(
    report_id: int,
    status_value: str = Query(..., regex="^(Reviewed|Dismissed)$"),
    _: bool = Depends(require_moderator),
    moderator_service: ModeratorService = Depends(get_moderator_service),
):
    """Update post report status to Reviewed or Dismissed. Moderator only."""
    return await moderator_service.update_post_report_status(report_id, status_value)


@router.get(
    "/reports/comments",
    response_model=List[CommentReportResponse],
    summary="Get all comment reports",
)
async def get_pending_comment_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    _: bool = Depends(require_moderator),
    moderator_service: ModeratorService = Depends(get_moderator_service),
):
    """Get all comment reports (pending, reviewed, dismissed). Moderator only."""
    return await moderator_service.get_pending_comment_reports(skip, limit)


@router.put(
    "/reports/comments/{report_id}/status",
    response_model=CommentReportResponse,
    summary="Update comment report status",
)
async def update_comment_report_status(
    report_id: int,
    status_value: str = Query(..., regex="^(Reviewed|Dismissed)$"),
    _: bool = Depends(require_moderator),
    moderator_service: ModeratorService = Depends(get_moderator_service),
):
    """Update comment report status to Reviewed or Dismissed. Moderator only."""
    return await moderator_service.update_comment_report_status(report_id, status_value)


# Note: Post and comment update/delete operations are now handled through common routes in posts and comments routers.
# Those routes automatically check if the user is the owner, admin, or moderator.
