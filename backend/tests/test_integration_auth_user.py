"""
End-to-end integration tests for authentication and user management.

This test file covers the complete flow:
1. Create a new user via API
2. Login with the created user
3. Access protected endpoints with the token
4. Change password
5. Login with new password
"""

import pytest
from httpx import AsyncClient


@pytest.mark.e2e
@pytest.mark.asyncio
class TestAuthUserE2E:
    """End-to-end tests for authentication and user creation flow."""

    async def test_complete_user_auth_flow(self, client: AsyncClient):
        """
        Test the complete user authentication flow:
        1. Create a new user
        2. Login with credentials
        3. Access protected endpoint (/users/me)
        4. Change password
        5. Login with new password
        6. Verify old password doesn't work
        """

        # Step 1: Create a new user
        user_data = {
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "InitialPassword123!",
        }

        create_response = await client.post(
            "/users/",
            data=user_data,
        )

        assert create_response.status_code == 201
        user_response = create_response.json()
        assert user_response["username"] == "integrationuser"
        assert user_response["email"] == "integration@example.com"
        assert user_response["is_active"] is True
        assert "id" in user_response
        user_id = user_response["id"]

        # Step 2: Login with the created user
        login_data = {
            "email": "integration@example.com",
            "password": "InitialPassword123!",
        }

        login_response = await client.post("/auth/login", json=login_data)

        assert login_response.status_code == 200
        login_result = login_response.json()
        assert "access_token" in login_result
        assert login_result["token_type"] == "bearer"
        assert login_result["user"]["username"] == "integrationuser"

        access_token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Step 3: Access protected endpoint to get current user
        me_response = await client.get("/users/me", headers=headers)

        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["id"] == user_id
        assert me_data["username"] == "integrationuser"
        assert me_data["email"] == "integration@example.com"

        # Step 4: Change password
        change_password_data = {
            "old_password": "InitialPassword123!",
            "new_password": "NewSecurePassword456!",
        }

        change_password_response = await client.post(
            "/auth/change-password",
            json=change_password_data,
            headers=headers,
        )

        assert change_password_response.status_code == 200
        change_result = change_password_response.json()
        assert change_result["message"] == "Password changed successfully"

        # Step 5: Login with new password
        new_login_data = {
            "email": "integration@example.com",
            "password": "NewSecurePassword456!",
        }

        new_login_response = await client.post("/auth/login", json=new_login_data)

        assert new_login_response.status_code == 200
        new_login_result = new_login_response.json()
        assert "access_token" in new_login_result
        assert new_login_result["user"]["username"] == "integrationuser"

        # Step 6: Verify old password doesn't work
        old_login_data = {
            "email": "integration@example.com",
            "password": "InitialPassword123!",  # Old password
        }

        old_login_response = await client.post("/auth/login", json=old_login_data)

        assert old_login_response.status_code == 401
        error_detail = old_login_response.json().get(
            "detail", old_login_response.json()
        )
        assert "Invalid username or password" in str(error_detail)

    async def test_create_user_duplicate_email(self, client: AsyncClient):
        """Test creating users with duplicate emails fails."""

        # Create first user
        user_data = {
            "username": "firstuser",
            "email": "duplicate@example.com",
            "password": "Password123!",
        }

        first_response = await client.post("/users/", data=user_data)
        assert first_response.status_code == 201

        # Try to create second user with same email
        user_data2 = {
            "username": "seconduser",
            "email": "duplicate@example.com",  # Same email
            "password": "Password123!",
        }

        second_response = await client.post("/users/", data=user_data2)
        assert second_response.status_code == 400
        error_detail = second_response.json().get("detail", second_response.json())
        assert "Email already registered" in str(error_detail)

    async def test_create_user_duplicate_username(self, client: AsyncClient):
        """Test creating users with duplicate usernames fails."""

        # Create first user
        user_data = {
            "username": "duplicateuser",
            "email": "user1@example.com",
            "password": "Password123!",
        }

        first_response = await client.post("/users/", data=user_data)
        assert first_response.status_code == 201

        # Try to create second user with same username
        user_data2 = {
            "username": "duplicateuser",  # Same username
            "email": "user2@example.com",
            "password": "Password123!",
        }

        second_response = await client.post("/users/", data=user_data2)
        assert second_response.status_code == 400
        error_detail = second_response.json().get("detail", second_response.json())
        assert "Username already taken" in str(error_detail)

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user fails."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "Password123!",
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        error_detail = response.json().get("detail", response.json())
        assert "Invalid username or password" in str(error_detail)

    async def test_access_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without authentication fails."""
        response = await client.get("/users/me")

        assert response.status_code == 401

    async def test_access_protected_endpoint_invalid_token(self, client: AsyncClient):
        """Test accessing protected endpoint with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token_here"}

        response = await client.get("/users/me", headers=headers)

        assert response.status_code == 401

    async def test_change_password_wrong_old_password(self, client: AsyncClient):
        """Test changing password with incorrect old password fails."""

        # Create and login user
        user_data = {
            "username": "pwdtestuser",
            "email": "pwdtest@example.com",
            "password": "OriginalPassword123!",
        }

        create_response = await client.post("/users/", data=user_data)
        assert create_response.status_code == 201

        login_data = {
            "email": "pwdtest@example.com",
            "password": "OriginalPassword123!",
        }

        login_response = await client.post("/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Try to change password with wrong old password
        change_password_data = {
            "old_password": "WrongPassword123!",
            "new_password": "NewPassword456!",
        }

        response = await client.post(
            "/auth/change-password",
            json=change_password_data,
            headers=headers,
        )

        assert response.status_code == 401
        error_detail = response.json().get("detail", response.json())
        assert "Invalid old password" in str(error_detail)

    async def test_update_user_profile(self, client: AsyncClient):
        """Test updating user profile (username)."""

        # Create and login user
        user_data = {
            "username": "updateuser",
            "email": "update@example.com",
            "password": "Password123!",
        }

        create_response = await client.post("/users/", data=user_data)
        assert create_response.status_code == 201

        login_data = {
            "email": "update@example.com",
            "password": "Password123!",
        }

        login_response = await client.post("/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Update username
        update_data = {"username": "updatedusername"}

        response = await client.put(
            "/users/",
            data=update_data,
            headers=headers,
        )

        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["username"] == "updatedusername"

        # Verify the change persists
        me_response = await client.get("/users/me", headers=headers)
        assert me_response.json()["username"] == "updatedusername"
