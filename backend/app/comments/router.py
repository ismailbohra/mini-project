# app/comments/router.py
from typing import List, Optional

import app.utils.redis as redis_utils
from app.auth.dependency import (
    get_current_user_id,
    get_current_user_id_optional,
    get_current_user_role,
)
from app.comments.dependency import get_comment_service
from app.comments.schema import (
    CommentCreate,
    CommentLikeResponse,
    CommentReportResponse,
    CommentResponse,
    CommentUpdate,
)
from app.comments.service import CommentService
from fastapi import APIRouter, Depends, Query, Response, status

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get(
    "/post/{post_id}",
    response_model=List[CommentResponse],
    summary="Get all comments for a post",
)
async def get_post_comments(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    comment_service: CommentService = Depends(get_comment_service),
    current_user_id: Optional[int] = Depends(get_current_user_id_optional),
    response: Response = None,
):
    """Get all top-level comments for a post with nested replies."""
    cache_key = f"comments:post:{post_id}"
    cached = await redis_utils.get_cache(cache_key)
    if cached:
        if response is not None:
            response.headers["X-Cache"] = "HIT"
        return [CommentResponse(**item) for item in cached]

    if response is not None:
        response.headers["X-Cache"] = "MISS"

    return await comment_service.get_post_comments(
        post_id, skip, limit, current_user_id
    )


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new comment",
)
async def create_comment(
    comment_data: CommentCreate,
    user_id: int = Depends(get_current_user_id),
    comment_service: CommentService = Depends(get_comment_service),
):
    """Create a new comment or reply."""
    return await comment_service.create_comment(user_id, comment_data, user_id)


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Update a comment",
)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    comment_service: CommentService = Depends(get_comment_service),
):
    """Update a comment. Owner, Admin, or Moderator can update."""
    return await comment_service.update_comment(
        comment_id, user_id, comment_data, user_id, user_role=user_role
    )


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment",
)
async def delete_comment(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    comment_service: CommentService = Depends(get_comment_service),
):
    """Delete a comment. Owner, Admin, or Moderator can delete."""
    await comment_service.delete_comment(comment_id, user_id, user_role=user_role)


# Comment Report endpoint
@router.post(
    "/{comment_id}/report",
    response_model=CommentReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report a comment",
)
async def report_comment(
    comment_id: int,
    reason: str = Query(..., min_length=1, max_length=500),
    user_id: int = Depends(get_current_user_id),
    comment_service: CommentService = Depends(get_comment_service),
):
    """Report a comment for review. User must be authenticated."""
    return await comment_service.report_comment(user_id, comment_id, reason)


@router.post(
    "/{comment_id}/like",
    response_model=CommentLikeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Like a comment",
)
async def like_comment(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    comment_service: CommentService = Depends(get_comment_service),
):
    """Like a comment."""
    return await comment_service.like_comment(user_id, comment_id)


@router.delete(
    "/{comment_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlike a comment",
)
async def unlike_comment(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    comment_service: CommentService = Depends(get_comment_service),
):
    """Remove like from a comment."""
    await comment_service.unlike_comment(user_id, comment_id)
