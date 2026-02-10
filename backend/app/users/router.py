from app.auth.dependency import get_current_user_id
from app.users.dependency import get_user_service
from app.users.schema import UserCreate, UserResponse, UserUpdate
from app.users.service import UserService
from fastapi import APIRouter, Depends, status

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


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate, service: UserService = Depends(get_user_service)
):
    """
    Create a new user
    """
    return await service.create_user(user_create)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    """
    Get a user by ID
    """
    return await service.get_user(user_id)


@router.put("/", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update a user
    """
    return await service.update_user(user_id, user_update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    """
    Delete a user
    """
    await service.delete_user(user_id)
