from typing import List, Optional

from app.users.interface import UserRepositoryInterface
from app.users.model import User
from app.users.schema import UserCreate, UserMentionResponse, UserUpdate
from app.utils.exceptions import (
    InvalidPasswordException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.utils.logging import get_logger
from app.utils.security import get_password_hash, validate_password

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
            import app.utils.redis as redis_utils

            cache_key = f"user:profile:{user_id}"
            cached = await redis_utils.get_cache(cache_key)
            if cached:
                from app.users.model import User

                user = User(**cached)
                return user

            user = await self.repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(message=f"User with id {user_id} not found")

            user_dict = {
                "id": user.id,
                "username": user.username,
                "role": user.role.value,
                "email": user.email,
                "profile_image": user.profile_image,
                "is_active": user.is_active,
                "is_deleted": user.is_deleted,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            }
            await redis_utils.set_cache(cache_key, user_dict, expire=1800)

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

            validate_password(user_create.password)

            user_data = user_create.model_dump()
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
            if profile_image:
                user_data["profile_image"] = profile_image

            user = await self.repository.create(user_data)
            logger.info(f"User created successfully: {user.email}")
            return user
        except (UserAlreadyExistsException, InvalidPasswordException):
            raise
        except Exception as e:
            logger.exception(f"Error creating user: {e}")
            raise

    async def update_user(
        self, user_id: int, user_update: UserUpdate, profile_image: Optional[str] = None
    ) -> User:
        try:
            # Fetch directly from database (bypass cache) to ensure the user is attached to the session
            user = await self.repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(message=f"User with id {user_id} not found")

            update_data = user_update.model_dump(exclude_unset=True)

            if "password" in update_data:
                validate_password(update_data["password"])
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

            import app.utils.redis as redis_utils

            await redis_utils.delete_cache(f"user:profile:{user_id}")

            logger.info(f"User {user_id} updated successfully")
            return updated_user
        except (
            UserNotFoundException,
            UserAlreadyExistsException,
            InvalidPasswordException,
        ):
            raise
        except Exception as e:
            logger.exception(f"Error updating user {user_id}: {e}")
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
            import app.utils.redis as redis_utils

            cache_key = f"search:mentions:{search_term}:{limit}"
            cached = await redis_utils.get_cache(cache_key)
            if cached:
                return [UserMentionResponse(**item) for item in cached]

            users = await self.repository.search_by_username(search_term, limit)
            result = [
                UserMentionResponse(
                    id=user.id, username=user.username, profile_image=user.profile_image
                )
                for user in users
            ]

            await redis_utils.set_cache(
                cache_key, [r.model_dump(mode="json") for r in result], expire=600
            )

            return result
        except Exception as e:
            logger.exception(f"Error searching users for mentions: {e}")
            raise
