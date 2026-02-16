"""
Unit tests for the users module.

Tests:
- Create user with valid data
- Create user with duplicate email
- Create user with duplicate username
- Get user by ID
- Get user not found
- Update user
- Get all users with pagination
- Search users for mentions
"""

import pytest
from app.users.model import RoleType, User
from app.users.repository import UserRepository
from app.users.schema import UserCreate, UserUpdate
from app.users.service import UserService
from app.utils.exceptions import UserAlreadyExistsException, UserNotFoundException
from app.utils.security import get_password_hash, verify_password
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def existing_user(db_session: AsyncSession) -> User:
    """Create an existing test user in the database."""
    user = User(
        username="existinguser",
        email="existing@example.com",
        hashed_password=get_password_hash("Password123!"),
        is_active=True,
        role=RoleType.USER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def multiple_users(db_session: AsyncSession) -> list[User]:
    """Create multiple test users for pagination and search tests."""
    users = []
    for i in range(5):
        user = User(
            username=f"user{i}",
            email=f"user{i}@example.com",
            hashed_password=get_password_hash("Password123!"),
            is_active=True,
            role=RoleType.USER,
        )
        db_session.add(user)
        users.append(user)

    await db_session.commit()
    for user in users:
        await db_session.refresh(user)

    return users


@pytest.fixture
def user_service(db_session: AsyncSession) -> UserService:
    """Create a UserService instance with test repository."""
    repository = UserRepository(db_session)
    return UserService(repository)


@pytest.mark.unit
@pytest.mark.asyncio
class TestUserService:
    """Test cases for UserService."""

    async def test_create_user_success(self, user_service: UserService):
        """Test creating a new user with valid data."""
        user_data = UserCreate(
            username="newuser",
            email="newuser@example.com",
            password="SecurePassword123!",
        )

        user = await user_service.create_user(user_data)

        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.is_active is True
        assert user.role == RoleType.USER
        assert verify_password("SecurePassword123!", user.hashed_password)

    async def test_create_user_with_profile_image(self, user_service: UserService):
        """Test creating a user with profile image."""
        user_data = UserCreate(
            username="imageuser", email="imageuser@example.com", password="Password123!"
        )
        profile_image = "uploads/users/profile.jpg"

        user = await user_service.create_user(user_data, profile_image=profile_image)

        assert user.profile_image == profile_image

    async def test_create_user_duplicate_email(
        self, user_service: UserService, existing_user: User
    ):
        """Test creating a user with duplicate email raises exception."""
        user_data = UserCreate(
            username="differentuser",
            email="existing@example.com",  # Duplicate email
            password="Password123!",
        )

        with pytest.raises(UserAlreadyExistsException) as exc_info:
            await user_service.create_user(user_data)

        assert "Email already registered" in str(exc_info.value)

    async def test_create_user_duplicate_username(
        self, user_service: UserService, existing_user: User
    ):
        """Test creating a user with duplicate username raises exception."""
        user_data = UserCreate(
            username="existinguser",  # Duplicate username
            email="newemail@example.com",
            password="Password123!",
        )

        with pytest.raises(UserAlreadyExistsException) as exc_info:
            await user_service.create_user(user_data)

        assert "Username already taken" in str(exc_info.value)

    async def test_get_user_success(
        self, user_service: UserService, existing_user: User
    ):
        """Test retrieving an existing user by ID."""
        user = await user_service.get_user(existing_user.id)

        assert user.id == existing_user.id
        assert user.username == existing_user.username
        assert user.email == existing_user.email

    async def test_get_user_not_found(self, user_service: UserService):
        """Test retrieving non-existent user raises exception."""
        with pytest.raises(UserNotFoundException) as exc_info:
            await user_service.get_user(9999)

        assert "User with id 9999 not found" in str(exc_info.value)

    async def test_update_user_username(
        self, user_service: UserService, existing_user: User
    ):
        """Test updating user username."""
        update_data = UserUpdate(username="updatedusername")

        updated_user = await user_service.update_user(existing_user.id, update_data)

        assert updated_user.username == "updatedusername"
        assert updated_user.email == existing_user.email

    async def test_update_user_password(
        self, user_service: UserService, existing_user: User
    ):
        """Test updating user password."""
        update_data = UserUpdate(password="NewPassword456!")

        updated_user = await user_service.update_user(existing_user.id, update_data)

        # Verify new password is hashed correctly
        assert verify_password("NewPassword456!", updated_user.hashed_password)

    async def test_update_user_with_profile_image(
        self, user_service: UserService, existing_user: User
    ):
        """Test updating user with profile image."""
        update_data = UserUpdate(username="updateduser")
        profile_image = "uploads/users/newprofile.jpg"

        updated_user = await user_service.update_user(
            existing_user.id, update_data, profile_image=profile_image
        )

        assert updated_user.profile_image == profile_image

    async def test_get_users_pagination(
        self, user_service: UserService, multiple_users: list[User]
    ):
        """Test retrieving users with pagination."""
        # Get first 3 users
        users_page1 = await user_service.get_users(skip=0, limit=3)
        assert len(users_page1) == 3

        # Get next 2 users
        users_page2 = await user_service.get_users(skip=3, limit=3)
        assert len(users_page2) == 2

        # Verify no overlap
        page1_ids = {user.id for user in users_page1}
        page2_ids = {user.id for user in users_page2}
        assert len(page1_ids.intersection(page2_ids)) == 0

    async def test_search_users_for_mentions(
        self, user_service: UserService, multiple_users: list[User]
    ):
        """Test searching users for mentions autocomplete."""
        results = await user_service.search_users_for_mentions("user", limit=10)

        assert len(results) == 5
        # All results should have username containing "user"
        for result in results:
            assert "user" in result.username.lower()

    async def test_search_users_for_mentions_with_limit(
        self, user_service: UserService, multiple_users: list[User]
    ):
        """Test searching users with limit."""
        results = await user_service.search_users_for_mentions("user", limit=3)

        assert len(results) == 3


@pytest.mark.unit
@pytest.mark.asyncio
class TestUserRepository:
    """Test cases for UserRepository."""

    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user in repository."""
        repository = UserRepository(db_session)
        user_data = {
            "username": "repouser",
            "email": "repo@example.com",
            "hashed_password": get_password_hash("Password123!"),
        }

        user = await repository.create(user_data)

        assert user.id is not None
        assert user.username == "repouser"
        assert user.email == "repo@example.com"

    async def test_get_by_id(self, db_session: AsyncSession, existing_user: User):
        """Test retrieving user by ID from repository."""
        repository = UserRepository(db_session)

        user = await repository.get_by_id(existing_user.id)

        assert user is not None
        assert user.id == existing_user.id

    async def test_get_by_email(self, db_session: AsyncSession, existing_user: User):
        """Test retrieving user by email from repository."""
        repository = UserRepository(db_session)

        user = await repository.get_by_email("existing@example.com")

        assert user is not None
        assert user.email == "existing@example.com"

    async def test_get_by_username(self, db_session: AsyncSession, existing_user: User):
        """Test retrieving user by username from repository."""
        repository = UserRepository(db_session)

        user = await repository.get_by_username("existinguser")

        assert user is not None
        assert user.username == "existinguser"

    async def test_get_all(self, db_session: AsyncSession, multiple_users: list[User]):
        """Test retrieving all users with pagination."""
        repository = UserRepository(db_session)

        users = await repository.get_all(skip=0, limit=10)

        assert len(users) >= 5  # At least the 5 we created

    async def test_update_user(self, db_session: AsyncSession, existing_user: User):
        """Test updating a user in repository."""
        repository = UserRepository(db_session)

        updated_user = await repository.update(
            existing_user, {"username": "updatedrepouser"}
        )

        assert updated_user.username == "updatedrepouser"

    async def test_get_by_usernames(
        self, db_session: AsyncSession, multiple_users: list[User]
    ):
        """Test retrieving multiple users by usernames."""
        repository = UserRepository(db_session)
        usernames = ["user0", "user2", "user4"]

        users = await repository.get_by_usernames(usernames)

        assert len(users) == 3
        retrieved_usernames = {user.username for user in users}
        assert retrieved_usernames == set(usernames)


@pytest.mark.unit
def test_user_model_validation():
    """Test User model validation and creation."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword123",
        role=RoleType.USER,
    )

    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == RoleType.USER
    # Default values are set by the database, not the model
    # These would be None until persisted and refreshed
