from typing import List

import app.utils.redis as redis_utils
from app.auth.dependency import get_current_user_id
from app.users.dependency import get_user_service
from app.users.schema import UserCreate, UserMentionResponse, UserResponse, UserUpdate
from app.users.service import UserService
from app.utils.upload import save_upload_file
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from pydantic import EmailStr

router = APIRouter(prefix="/users", tags=["User"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user",
)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Get current user information including:
    - User details (id, username, email)
    - Active status
    - Assigned roles

    Requires valid JWT token in Authorization header.
    """
    return await service.get_user(user_id)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    profile_image: UploadFile | None = File(None),
    service: UserService = Depends(get_user_service),
):
    """Create a new user (supports optional profile image)."""
    image_path = None
    if profile_image:
        image_path = save_upload_file(profile_image, subdir="users")
    user_create = UserCreate(username=username, email=email, password=password)
    return await service.create_user(user_create, profile_image=image_path)


@router.get("/search/mentions", response_model=List[UserMentionResponse])
async def search_users_for_mentions(
    q: str = Query(..., min_length=1, description="Search query for username"),
    limit: int = Query(10, ge=1, le=20),
    service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user_id),
    response: Response = None,
):
    """
    Search users by username for @mention autocomplete.

    Returns a list of users matching the search query with:
    - User ID
    - Username
    - Profile image

    Used for mention suggestions when typing @username in posts/comments.
    """
    cache_key = f"search:mentions:{q}:{limit}"
    cached = await redis_utils.get_cache(cache_key)
    if cached:
        if response is not None:
            response.headers["X-Cache"] = "HIT"
        return [UserMentionResponse(**item) for item in cached]

    if response is not None:
        response.headers["X-Cache"] = "MISS"

    return await service.search_users_for_mentions(q, limit)


@router.put("", response_model=UserResponse)
async def update_user(
    username: str | None = Form(None),
    password: str | None = Form(None),
    bio: str | None = Form(None),
    profile_image: UploadFile | None = File(None),
    service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user_id),
):
    """Update the authenticated user (supports optional profile image)."""
    image_path = None
    if profile_image:
        image_path = save_upload_file(profile_image, subdir="users")
    update_payload = {}
    if username is not None:
        update_payload["username"] = username
    if password is not None:
        update_payload["password"] = password
    if bio is not None:
        update_payload["bio"] = bio
    
    user_update = UserUpdate(**update_payload)
    return await service.update_user(user_id, user_update, profile_image=image_path)
