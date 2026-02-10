# app/posts/router.py
from typing import List

from app.auth.dependency import get_current_user_id
from app.posts.dependency import get_post_service
from app.posts.schema import (
    PostCreate,
    PostLikeResponse,
    PostReportResponse,
    PostResponse,
    PostUpdate,
)
from app.posts.service import PostService
from fastapi import APIRouter, Depends, Query, status

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
)
async def create_post(
    post_data: PostCreate,
    user_id: int = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    """Create a new post with tags. User must be authenticated."""
    return await post_service.create_post(user_id, post_data)


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get a post by ID",
)
async def get_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
):
    """Get a single post by ID."""
    return await post_service.get_post(post_id)


@router.get(
    "/",
    response_model=List[PostResponse],
    summary="Get all posts",
)
async def get_all_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    post_service: PostService = Depends(get_post_service),
):
    """Get all posts with pagination."""
    return await post_service.get_all_posts(skip, limit)


@router.get(
    "/user/me",
    response_model=List[PostResponse],
    summary="Get current user's posts",
)
async def get_my_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    """Get all posts by the authenticated user."""
    return await post_service.get_user_posts(user_id, skip, limit)


@router.get(
    "/user/{author_id}",
    response_model=List[PostResponse],
    summary="Get posts by user ID",
)
async def get_user_posts(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    post_service: PostService = Depends(get_post_service),
):
    """Get all posts by a specific user."""
    return await post_service.get_user_posts(author_id, skip, limit)


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="Update a post",
)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    user_id: int = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    """Update a post. Only the author can update their own posts."""
    return await post_service.update_post(post_id, user_id, post_data)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a post",
)
async def delete_post(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    """Delete a post. Only the author can delete their own posts."""
    await post_service.delete_post(post_id, user_id)


# Post Like endpoints
@router.post(
    "/{post_id}/like",
    response_model=PostLikeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Like a post",
)
async def like_post(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    """Like a post. User must be authenticated."""
    return await post_service.like_post(user_id, post_id)


@router.delete(
    "/{post_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlike a post",
)
async def unlike_post(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    """Remove like from a post. User must be authenticated."""
    await post_service.unlike_post(user_id, post_id)


@router.get(
    "/{post_id}/likes/count",
    response_model=int,
    summary="Get post likes count",
)
async def get_post_likes_count(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
):
    """Get the count of likes for a post."""
    return await post_service.get_post_likes_count(post_id)


# Post Report endpoint
@router.post(
    "/{post_id}/report",
    response_model=PostReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report a post",
)
async def report_post(
    post_id: int,
    reason: str = Query(..., min_length=1, max_length=500),
    user_id: int = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    """Report a post for review. User must be authenticated."""
    return await post_service.report_post(user_id, post_id, reason)
