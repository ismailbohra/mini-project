# app/posts/router.py
import json
from typing import List, Optional

import app.utils.redis as redis_utils
from app.auth.dependency import (
    get_current_user_id,
    get_current_user_id_optional,
    get_current_user_role,
)
from app.posts.dependency import get_post_service
from app.posts.schema import (
    PostCreate,
    PostLikeResponse,
    PostListResponse,
    PostReportResponse,
    PostResponse,
    PostUpdate,
    TagResponse,
)
from app.posts.service import PostService
from app.utils.upload import save_upload_file
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get(
    "/search/suggestions",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Get search suggestions",
)
async def get_search_suggestions(
    search: str = Query(
        ..., min_length=2, description="Search term (minimum 2 characters)"
    ),
    limit: int = Query(10, ge=1, le=20),
    post_service: PostService = Depends(get_post_service),
    response: Response = None,
):
    """Get search suggestions based on partial match in titles, authors, and tags."""
    cache_key = f"search:suggestions:{search}:{limit}"
    cached = await redis_utils.get_cache(cache_key)
    if cached:
        if response is not None:
            response.headers["X-Cache"] = "HIT"
        return cached

    if response is not None:
        response.headers["X-Cache"] = "MISS"

    return await post_service.search_suggestions(search, limit)


@router.get(
    "/tags",
    response_model=List[TagResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all tags",
)
async def get_all_tags(
    post_service: PostService = Depends(get_post_service),
    response: Response = None,
):
    """Return all tags."""
    cache_key = "tags:all"
    cached = await redis_utils.get_cache(cache_key)
    if cached:
        if response is not None:
            response.headers["X-Cache"] = "HIT"
        return [TagResponse(**item) for item in cached]

    if response is not None:
        response.headers["X-Cache"] = "MISS"

    return await post_service.get_all_tags()


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
)
async def create_post(
    title: str = Form(...),
    description: str = Form(...),
    tags: str = Form("[]"),
    image: UploadFile | None = File(None),
    user_id: int = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    """Create a new post (supports optional image)."""
    try:
        tags_list = json.loads(tags)
    except Exception:
        tags_list = []

    image_path = None
    if image:
        image_path = save_upload_file(image, subdir="posts")

    post_data = PostCreate(title=title, description=description, tags=tags_list)
    return await post_service.create_post(
        user_id, post_data, user_id, image_path=image_path
    )


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get a post by ID",
)
async def get_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
    current_user_id: Optional[int] = Depends(get_current_user_id_optional),
    response: Response = None,
):
    """Get a single post by ID."""
    cache_key = f"post:{post_id}"
    cached = await redis_utils.get_cache(cache_key)
    if cached:
        if response is not None:
            response.headers["X-Cache"] = "HIT"
        return PostResponse(**cached)

    if response is not None:
        response.headers["X-Cache"] = "MISS"

    return await post_service.get_post(post_id, current_user_id)


@router.get(
    "/",
    response_model=PostListResponse,
    summary="Get all posts",
)
async def get_all_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(
        None, description="Search in title, description, author name, and tags"
    ),
    tags: Optional[List[str]] = Query(
        None, alias="tags[]", description="Filter by tag names"
    ),
    sort_by: str = Query(
        "created_at", description="Sort by field (created_at, updated_at)"
    ),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    post_service: PostService = Depends(get_post_service),
    current_user_id: Optional[int] = Depends(get_current_user_id_optional),
    response: Response = None,
):
    """Get all posts with search, filter, and sort capabilities."""
    # Validate sort_by parameter
    valid_sort_fields = ["created_at", "updated_at"]
    if sort_by not in valid_sort_fields:
        sort_by = "created_at"

    # Validate sort_order parameter
    if sort_order.lower() not in ["asc", "desc"]:
        sort_order = "desc"

    search_str = search or ""
    tags_str = ",".join(sorted(tags)) if tags else ""
    cache_key = (
        f"posts:list:{skip}:{limit}:{search_str}:{tags_str}:{sort_by}:{sort_order}"
    )
    cached = await redis_utils.get_cache(cache_key)
    if cached:
        if response is not None:
            response.headers["X-Cache"] = "HIT"
        return PostListResponse(**cached)

    if response is not None:
        response.headers["X-Cache"] = "MISS"

    return await post_service.get_all_posts(
        skip, limit, current_user_id, search, tags, sort_by, sort_order
    )


@router.get(
    "/user/me",
    response_model=PostListResponse,
    summary="Get current user's posts",
)
async def get_my_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
    response: Response = None,
):
    """Get all posts by the authenticated user."""
    cache_key = f"posts:user:{user_id}:{skip}:{limit}"
    cached = await redis_utils.get_cache(cache_key)
    if cached:
        if response is not None:
            response.headers["X-Cache"] = "HIT"
        return PostListResponse(**cached)

    if response is not None:
        response.headers["X-Cache"] = "MISS"

    return await post_service.get_user_posts(user_id, skip, limit, user_id)


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="Update a post",
)
async def update_post(
    post_id: int,
    title: str | None = Form(None),
    description: str | None = Form(None),
    tags: str | None = Form(None),
    image: UploadFile | None = File(None),
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    post_service: PostService = Depends(get_post_service),
):
    """Update a post (supports optional image). Owner, Admin, or Moderator can update."""
    update_payload = {}
    if title is not None:
        update_payload["title"] = title
    if description is not None:
        update_payload["description"] = description
    if tags is not None:
        try:
            update_payload["tags"] = json.loads(tags)
        except Exception:
            update_payload["tags"] = None

    image_path = None
    if image:
        image_path = save_upload_file(image, subdir="posts")

    post_update = PostUpdate(**update_payload)
    return await post_service.update_post(
        post_id,
        user_id,
        post_update,
        user_id,
        image_path=image_path,
        user_role=user_role,
    )


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a post",
)
async def delete_post(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    post_service: PostService = Depends(get_post_service),
):
    """Delete a post. Owner, Admin, or Moderator can delete."""
    await post_service.delete_post(post_id, user_id, user_role=user_role)


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
