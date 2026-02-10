from typing import List

from app.users.dependency import get_user_service
from app.users.schema import RoleAssign, UserCreate, UserResponse, UserUpdate
from app.users.service import UserService
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service),
):
    """
    Get all users
    """
    return await service.get_users(skip=skip, limit=limit)


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


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service),
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


@router.patch("/{user_id}/role", response_model=UserResponse)
async def assign_role(
    user_id: int,
    role_assign: RoleAssign,
    service: UserService = Depends(get_user_service),
):
    """
    Assign a role to a user.
    Roles: Admin, User, moderator
    """
    return await service.assign_role(user_id, role_assign)
