"""
Unit tests for the authentication module.

Tests:
- Login with valid credentials
- Login with invalid credentials
- Login with inactive user
- Change password with valid old password
- Change password with invalid old password
- Get current user
"""

import pytest
from app.auth.repository import AuthRepository
from app.auth.schema import ChangePasswordRequest, UserLoginRequest
from app.auth.service import AuthService
from app.users.model import RoleType, User
from app.utils.exceptions import NotFoundException, UnauthorizedException
from app.utils.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user in the database."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        role=RoleType.USER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def inactive_user(db_session: AsyncSession) -> User:
    """Create an inactive test user in the database."""
    user = User(
        username="inactiveuser",
        email="inactive@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=False,
        role=RoleType.USER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_service(db_session: AsyncSession) -> AuthService:
    """Create an AuthService instance with test repository."""
    repository = AuthRepository(db_session)
    return AuthService(repository)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthService:
    """Test cases for AuthService."""

    async def test_login_success(self, auth_service: AuthService, test_user: User):
        """Test successful login with valid credentials."""
        request = UserLoginRequest(
            email="testuser@example.com", password="TestPassword123!"
        )

        response = await auth_service.login(request)

        assert response.access_token is not None
        assert response.token_type == "bearer"
        assert response.user.id == test_user.id
        assert response.user.email == test_user.email
        assert response.user.username == test_user.username

    async def test_login_invalid_email(self, auth_service: AuthService):
        """Test login with non-existent email."""
        request = UserLoginRequest(
            email="nonexistent@example.com", password="TestPassword123!"
        )

        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.login(request)

        assert "Invalid username or password" in str(exc_info.value)

    async def test_login_invalid_password(
        self, auth_service: AuthService, test_user: User
    ):
        """Test login with incorrect password."""
        request = UserLoginRequest(
            email="testuser@example.com", password="WrongPassword123!"
        )

        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.login(request)

        assert "Invalid username or password" in str(exc_info.value)

    async def test_login_inactive_user(
        self, auth_service: AuthService, inactive_user: User
    ):
        """Test login with inactive user account."""
        request = UserLoginRequest(
            email="inactive@example.com", password="TestPassword123!"
        )

        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.login(request)

        assert "User account is inactive" in str(exc_info.value)

    async def test_change_password_success(
        self, auth_service: AuthService, test_user: User
    ):
        """Test successful password change."""
        request = ChangePasswordRequest(
            old_password="TestPassword123!", new_password="NewPassword456!"
        )

        response = await auth_service.change_password(test_user.id, request)

        assert response["message"] == "Password changed successfully"

        # Verify new password works
        login_request = UserLoginRequest(
            email="testuser@example.com", password="NewPassword456!"
        )
        login_response = await auth_service.login(login_request)
        assert login_response.access_token is not None

    async def test_change_password_invalid_old_password(
        self, auth_service: AuthService, test_user: User
    ):
        """Test password change with incorrect old password."""
        request = ChangePasswordRequest(
            old_password="WrongPassword123!", new_password="NewPassword456!"
        )

        with pytest.raises(UnauthorizedException) as exc_info:
            await auth_service.change_password(test_user.id, request)

        assert "Invalid old password" in str(exc_info.value)

    async def test_change_password_user_not_found(self, auth_service: AuthService):
        """Test password change for non-existent user."""
        request = ChangePasswordRequest(
            old_password="TestPassword123!", new_password="NewPassword456!"
        )

        with pytest.raises(NotFoundException) as exc_info:
            await auth_service.change_password(9999, request)

        assert "User not found" in str(exc_info.value)

    async def test_get_current_user_success(
        self, auth_service: AuthService, test_user: User
    ):
        """Test retrieving current user information."""
        response = await auth_service.get_current_user(test_user.id)

        assert response.id == test_user.id
        assert response.email == test_user.email
        assert response.username == test_user.username
        assert response.is_active is True

    async def test_get_current_user_not_found(self, auth_service: AuthService):
        """Test retrieving non-existent user."""
        with pytest.raises(NotFoundException) as exc_info:
            await auth_service.get_current_user(9999)

        assert "User not found" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthRepository:
    """Test cases for AuthRepository."""

    async def test_get_user_by_email(self, db_session: AsyncSession, test_user: User):
        """Test retrieving user by email."""
        repository = AuthRepository(db_session)

        user = await repository.get_user_by_email("testuser@example.com")

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    async def test_get_user_by_email_not_found(self, db_session: AsyncSession):
        """Test retrieving non-existent user by email."""
        repository = AuthRepository(db_session)

        user = await repository.get_user_by_email("nonexistent@example.com")

        assert user is None

    async def test_get_user_by_id(self, db_session: AsyncSession, test_user: User):
        """Test retrieving user by ID."""
        repository = AuthRepository(db_session)

        user = await repository.get_user_by_id(test_user.id)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    async def test_update_user_password(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test updating user password."""
        repository = AuthRepository(db_session)
        new_password_hash = get_password_hash("NewPassword456!")

        await repository.update_user_password(test_user, new_password_hash)

        # Refresh and verify
        await db_session.refresh(test_user)
        assert test_user.hashed_password == new_password_hash
