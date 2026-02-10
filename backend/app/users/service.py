from typing import List

from app.config.security import get_password_hash
from app.users.interface import UserRepositoryInterface
from app.users.model import User, UserRole
from app.users.schema import RoleAssign, UserCreate, UserUpdate
from app.utils.exceptions import UserAlreadyExistsException, UserNotFoundException


class UserService:
    def __init__(self, repository: UserRepositoryInterface):
        self.repository = repository

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return await self.repository.get_all(skip, limit)

    async def get_user(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(detail=f"User with id {user_id} not found")
        return user

    async def create_user(self, user_create: UserCreate) -> User:
        existing_user = await self.repository.get_by_email(user_create.email)
        if existing_user:
            raise UserAlreadyExistsException(detail="Email already registered")

        existing_username = await self.repository.get_by_username(user_create.username)
        if existing_username:
            raise UserAlreadyExistsException(detail="Username already taken")

        user_data = user_create.model_dump()
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

        return await self.repository.create(user_data)

    async def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        user = await self.get_user(user_id)

        update_data = user_update.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        if "email" in update_data and update_data["email"] != user.email:
            existing_user = await self.repository.get_by_email(update_data["email"])
            if existing_user:
                raise UserAlreadyExistsException(detail="Email already registered")

        if "username" in update_data and update_data["username"] != user.username:
            existing_username = await self.repository.get_by_username(
                update_data["username"]
            )
            if existing_username:
                raise UserAlreadyExistsException(detail="Username already taken")

        return await self.repository.update(user, update_data)

    async def delete_user(self, user_id: int) -> None:
        user = await self.get_user(user_id)
        await self.repository.delete(user)

    async def assign_role(self, user_id: int, role_assign: RoleAssign) -> User:
        user = await self.get_user(user_id)
        return await self.repository.update(user, {"role": role_assign.role})
