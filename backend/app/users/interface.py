from abc import ABC, abstractmethod
from typing import List, Optional

from app.users.model import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create(self, user_data: dict) -> User:
        pass

    @abstractmethod
    async def update(self, user: User, update_data: dict) -> User:
        pass

    @abstractmethod
    async def search_by_username(self, search_term: str, limit: int = 10) -> List[User]:
        pass

    @abstractmethod
    async def get_by_usernames(self, usernames: List[str]) -> List[User]:
        pass
