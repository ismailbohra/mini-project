# app/comments/router.py
from typing import List

from app.auth.dependency import get_current_user_id
from app.comments.dependency import get_comment_service
from app.comments.schema import (
    CommentCreate,
    CommentLikeResponse,
    CommentResponse,
    CommentUpdate,
)
from app.comments.service import CommentService
from fastapi import APIRouter, Depends, Query, status

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Get a comment by ID",
)
async def get_comment(
    comment_id: int,
    comment_service: CommentService = Depends(get_comment_service),
):
    """Get a single comment by ID with all nested replies."""
    return await comment_service.get_comment(comment_id)


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
):
    """Get all top-level comments for a post with nested replies."""
    return await comment_service.get_post_comments(post_id, skip, limit)


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
    return await comment_service.create_comment(user_id, comment_data)


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Update a comment",
)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    user_id: int = Depends(get_current_user_id),
    comment_service: CommentService = Depends(get_comment_service),
):
    """Update a comment. Only the author can update their own comments."""
    return await comment_service.update_comment(comment_id, user_id, comment_data)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment",
)
async def delete_comment(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    comment_service: CommentService = Depends(get_comment_service),
):
    """Delete a comment. Only the author can delete their own comments."""
    await comment_service.delete_comment(comment_id, user_id)


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
