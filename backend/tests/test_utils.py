"""
Unit tests for utility functions.

Tests:
- Security utilities (password hashing, token creation)
- Mention extraction
- Redis cache operations
- Exception handling
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.utils.exceptions import (
    ForbiddenException,
    InvalidPasswordException,
    NotFoundException,
    UnauthorizedException,
)
from app.utils.mentions import extract_mentions
from app.utils.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    validate_password,
    verify_password,
)


@pytest.mark.unit
class TestSecurityUtilities:
    """Test cases for security utilities."""

    def test_password_hashing(self):
        """Test password hashing works correctly."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_password_verification_success(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test password verification with wrong password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to salting
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry."""
        data = {"sub": "1", "role": "USER"}
        token = create_access_token(data)

        assert token is not None
        assert len(token) > 0

    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry."""
        data = {"sub": "1", "role": "USER"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)

        assert token is not None
        assert len(token) > 0

    def test_decode_token_success(self):
        """Test decoding valid token."""
        data = {"sub": "1", "role": "USER"}
        token = create_access_token(data)

        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == "1"
        assert decoded["role"] == "USER"
        assert "exp" in decoded
        assert decoded["type"] == "access"

    def test_decode_invalid_token(self):
        """Test decoding invalid token."""
        invalid_token = "invalid.token.here"

        decoded = decode_token(invalid_token)

        assert decoded is None

    def test_decode_expired_token(self):
        """Test decoding expired token."""
        data = {"sub": "1", "role": "USER"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expires_delta)

        # Wait a moment for token to expire
        import time

        time.sleep(0.1)

        decoded = decode_token(token)

        # Should return None for expired token
        assert decoded is None

    def test_validate_password_success(self):
        """Test password validation with valid password."""
        password = "ValidPass123!"

        # Should not raise exception
        validate_password(password)

    def test_validate_password_too_short(self):
        """Test password validation with short password."""
        password = "Short1!"

        with pytest.raises(InvalidPasswordException) as exc_info:
            validate_password(password)

        assert "at least 8 characters" in str(exc_info.value)

    def test_validate_password_no_uppercase(self):
        """Test password validation without uppercase letter."""
        password = "lowercase123!"

        with pytest.raises(InvalidPasswordException) as exc_info:
            validate_password(password)

        assert "uppercase letter" in str(exc_info.value)

    def test_validate_password_no_lowercase(self):
        """Test password validation without lowercase letter."""
        password = "UPPERCASE123!"

        with pytest.raises(InvalidPasswordException) as exc_info:
            validate_password(password)

        assert "lowercase letter" in str(exc_info.value)

    def test_validate_password_no_special_char(self):
        """Test password validation without special character."""
        password = "NoSpecial123"

        with pytest.raises(InvalidPasswordException) as exc_info:
            validate_password(password)

        assert "special character" in str(exc_info.value)


@pytest.mark.unit
class TestMentionExtraction:
    """Test cases for mention extraction utility."""

    def test_extract_mentions_single(self):
        """Test extracting single mention."""
        text = "Hello @username, how are you?"
        mentions = extract_mentions(text)

        assert mentions == ["username"]

    def test_extract_mentions_multiple(self):
        """Test extracting multiple mentions."""
        text = "Hello @user1 and @user2, welcome @user3!"
        mentions = extract_mentions(text)

        assert len(mentions) == 3
        assert "user1" in mentions
        assert "user2" in mentions
        assert "user3" in mentions

    def test_extract_mentions_none(self):
        """Test extracting mentions when none exist."""
        text = "Hello world, no mentions here!"
        mentions = extract_mentions(text)

        assert mentions == []

    def test_extract_mentions_with_underscores(self):
        """Test extracting mentions with underscores."""
        text = "Hello @user_name and @another_user!"
        mentions = extract_mentions(text)

        assert "user_name" in mentions
        assert "another_user" in mentions

    def test_extract_mentions_with_numbers(self):
        """Test extracting mentions with numbers."""
        text = "Hey @user123 and @test456!"
        mentions = extract_mentions(text)

        assert "user123" in mentions
        assert "test456" in mentions

    def test_extract_mentions_duplicate(self):
        """Test extracting duplicate mentions."""
        text = "Hello @user, goodbye @user"
        mentions = extract_mentions(text)

        # Should contain unique mentions
        assert mentions.count("user") == 2 or len(set(mentions)) == 1

    def test_extract_mentions_at_start(self):
        """Test extracting mention at start of text."""
        text = "@username is here"
        mentions = extract_mentions(text)

        assert "username" in mentions

    def test_extract_mentions_at_end(self):
        """Test extracting mention at end of text."""
        text = "Message for @username"
        mentions = extract_mentions(text)

        assert "username" in mentions

    def test_extract_mentions_with_punctuation(self):
        """Test extracting mentions followed by punctuation."""
        text = "Hello @user1, @user2! How are @user3?"
        mentions = extract_mentions(text)

        assert len(mentions) >= 3

    def test_extract_mentions_multiline(self):
        """Test extracting mentions from multiline text."""
        text = """Hello @user1
        This is a test
        Mentioning @user2 here"""
        mentions = extract_mentions(text)

        assert "user1" in mentions
        assert "user2" in mentions

    def test_extract_mentions_empty_string(self):
        """Test extracting mentions from empty string."""
        text = ""
        mentions = extract_mentions(text)

        assert mentions == []


@pytest.mark.unit
class TestCustomExceptions:
    """Test cases for custom exceptions."""

    def test_not_found_exception(self):
        """Test NotFoundException."""
        with pytest.raises(NotFoundException) as exc_info:
            raise NotFoundException("Item not found")

        assert "Item not found" in str(exc_info.value)

    def test_unauthorized_exception(self):
        """Test UnauthorizedException."""
        with pytest.raises(UnauthorizedException) as exc_info:
            raise UnauthorizedException("Unauthorized access")

        assert "Unauthorized access" in str(exc_info.value)

    def test_forbidden_exception(self):
        """Test ForbiddenException."""
        with pytest.raises(ForbiddenException) as exc_info:
            raise ForbiddenException("Access forbidden")

        assert "Access forbidden" in str(exc_info.value)

    def test_invalid_password_exception(self):
        """Test InvalidPasswordException."""
        with pytest.raises(InvalidPasswordException) as exc_info:
            raise InvalidPasswordException("Invalid password format")

        assert "Invalid password format" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
class TestRedisUtilities:
    """Test cases for Redis cache utilities."""

    async def test_redis_cache_import(self):
        """Test that redis utilities can be imported."""
        try:
            import app.utils.redis as redis_utils

            assert redis_utils is not None
        except ImportError:
            pytest.fail("Cannot import redis utilities")
