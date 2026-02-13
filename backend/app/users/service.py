from typing import List, Optional

from app.config.security import get_password_hash
from app.users.interface import UserRepositoryInterface
from app.users.model import User
from app.users.schema import UserCreate, UserMentionResponse, UserUpdate
from app.utils.exceptions import UserAlreadyExistsException, UserNotFoundException
from app.utils.logging import get_logger

logger = get_logger(__name__)


class UserService:
    def __init__(self, repository: UserRepositoryInterface):
        self.repository = repository

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            return await self.repository.get_all(skip, limit)
        except Exception as e:
            logger.exception(f"Error fetching users: {e}")
            raise

    async def get_user(self, user_id: int) -> User:
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(message=f"User with id {user_id} not found")
            return user
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.exception(f"Error fetching user {user_id}: {e}")
            raise

    async def create_user(
        self, user_create: UserCreate, profile_image: Optional[str] = None
    ) -> User:
        try:
            existing_user = await self.repository.get_by_email(user_create.email)
            if existing_user:
                raise UserAlreadyExistsException(message="Email already registered")

            existing_username = await self.repository.get_by_username(
                user_create.username
            )
            if existing_username:
                raise UserAlreadyExistsException(message="Username already taken")

            user_data = user_create.model_dump()
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
            if profile_image:
                user_data["profile_image"] = profile_image

            user = await self.repository.create(user_data)
            logger.info(f"User created successfully: {user.email}")
            return user
        except UserAlreadyExistsException:
            raise
        except Exception as e:
            logger.exception(f"Error creating user: {e}")
            raise

    async def update_user(
        self, user_id: int, user_update: UserUpdate, profile_image: Optional[str] = None
    ) -> User:
        try:
            user = await self.get_user(user_id)

            update_data = user_update.model_dump(exclude_unset=True)

            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(
                    update_data.pop("password")
                )

            if "email" in update_data and update_data["email"] != user.email:
                existing_user = await self.repository.get_by_email(update_data["email"])
                if existing_user:
                    raise UserAlreadyExistsException(message="Email already registered")

            if "username" in update_data and update_data["username"] != user.username:
                existing_username = await self.repository.get_by_username(
                    update_data["username"]
                )
                if existing_username:
                    raise UserAlreadyExistsException(message="Username already taken")

            if profile_image:
                update_data["profile_image"] = profile_image

            updated_user = await self.repository.update(user, update_data)
            logger.info(f"User {user_id} updated successfully")
            return updated_user
        except (UserNotFoundException, UserAlreadyExistsException):
            raise
        except Exception as e:
            logger.exception(f"Error updating user {user_id}: {e}")
            raise

    async def delete_user(self, user_id: int) -> None:
        try:
            user = await self.get_user(user_id)
            await self.repository.delete(user)
            logger.info(f"User {user_id} deleted successfully")
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.exception(f"Error deleting user {user_id}: {e}")
            raise

    async def search_users_for_mentions(
        self, search_term: str, limit: int = 10
    ) -> List[UserMentionResponse]:
        """
        Search users by username for mention autocomplete.

        Args:
            search_term: The search query (partial username)
            limit: Maximum number of results to return

        Returns:
            List of UserMentionResponse with id, username, and profile_image
        """
        try:
            users = await self.repository.search_by_username(search_term, limit)
            return [
                UserMentionResponse(
                    id=user.id, username=user.username, profile_image=user.profile_image
                )
                for user in users
            ]
        except Exception as e:
            logger.exception(f"Error searching users for mentions: {e}")
            raise
