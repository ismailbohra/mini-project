# app/moderator/router.py
from typing import List

from app.auth.dependency import require_moderator
from app.comments.schema import CommentReportResponse, CommentResponse, CommentUpdate
from app.moderator.dependency import get_moderator_service
from app.moderator.service import ModeratorService
from app.posts.schema import PostReportResponse, PostResponse, PostUpdate
from fastapi import APIRouter, Depends, Query, status

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


# Post Management
@router.get(
    "/posts",
    response_model=List[PostResponse],
    summary="Get all posts",
)
async def get_all_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    _: bool = Depends(require_moderator),
    moderator_service: ModeratorService = Depends(get_moderator_service),
):
    """Get all posts. Moderator only."""
    return await moderator_service.get_all_posts(skip, limit)


@router.put(
    "/posts/{post_id}",
    response_model=PostResponse,
    summary="Update any post",
)
async def update_any_post(
    post_id: int,
    post_data: PostUpdate,
    _: bool = Depends(require_moderator),
    moderator_service: ModeratorService = Depends(get_moderator_service),
):
    """Update any post. Moderator privilege."""
    return await moderator_service.update_any_post(post_id, post_data)


@router.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete any post",
)
async def delete_any_post(
    post_id: int,
    report_id: int = Query(None, description="Optional report ID to mark as reviewed"),
    _: bool = Depends(require_moderator),
    moderator_service: ModeratorService = Depends(get_moderator_service),
):
    """Delete any post. Moderator privilege. If report_id is provided, marks the report as reviewed."""
    await moderator_service.delete_any_post(post_id, report_id)


# Comment Management
@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    summary="Update any comment",
)
async def update_any_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    _: bool = Depends(require_moderator),
    moderator_service: ModeratorService = Depends(get_moderator_service),
):
    """Update any comment. Moderator privilege."""
    return await moderator_service.update_any_comment(comment_id, comment_data)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete any comment",
)
async def delete_any_comment(
    comment_id: int,
    report_id: int = Query(None, description="Optional report ID to mark as reviewed"),
    _: bool = Depends(require_moderator),
    moderator_service: ModeratorService = Depends(get_moderator_service),
):
    """Delete any comment. Moderator privilege. If report_id is provided, marks the report as reviewed."""
    await moderator_service.delete_any_comment(comment_id, report_id)
