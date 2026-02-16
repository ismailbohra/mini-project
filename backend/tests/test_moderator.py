"""
Unit tests for the moderator module.

Tests:
- Get pending post reports
- Update post report status
- Get pending comment reports
- Update comment report status
- Delete post
- Delete comment
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.moderator.service import ModeratorService
from app.utils.exceptions import NotFoundException


@pytest.fixture
def mock_post_repository():
    """Create a mock post repository."""
    repository = AsyncMock()
    return repository


@pytest.fixture
def mock_comment_repository():
    """Create a mock comment repository."""
    repository = AsyncMock()
    return repository


@pytest.fixture
def moderator_service(mock_post_repository, mock_comment_repository):
    """Create a ModeratorService instance with mock repositories."""
    return ModeratorService(mock_post_repository, mock_comment_repository)


@pytest.fixture
def test_post_report():
    """Create a test post report."""
    report = MagicMock()
    report.id = 1
    report.user_id = 1
    report.post_id = 1
    report.reason = "Inappropriate content"
    report.status = MagicMock()
    report.status.value = "PENDING"
    report.created_at = "2024-01-01T00:00:00"
    report.reviewed_at = None
    report.post = MagicMock()
    report.post.title = "Test Post"
    report.post.author_id = 2
    report.user = MagicMock()
    report.user.username = "reporter_user"
    return report


@pytest.fixture
def test_comment_report():
    """Create a test comment report."""
    report = MagicMock()
    report.id = 1
    report.user_id = 1
    report.comment_id = 1
    report.reason = "Spam"
    report.status = MagicMock()
    report.status.value = "PENDING"
    report.created_at = "2024-01-01T00:00:00"
    report.reviewed_at = None
    report.comment = MagicMock()
    report.comment.title = "Test Comment"
    report.comment.description = "Comment description"
    report.comment.author_id = 2
    report.comment.author = MagicMock()
    report.comment.author.username = "comment_author"
    report.user = MagicMock()
    report.user.username = "reporter_user"
    return report


@pytest.mark.unit
@pytest.mark.asyncio
class TestModeratorService:
    """Test cases for ModeratorService."""

    async def test_get_pending_post_reports_success(
        self, moderator_service, test_post_report
    ):
        """Test getting pending post reports successfully."""
        moderator_service.post_repository.get_pending_post_reports.return_value = [
            test_post_report
        ]

        result = await moderator_service.get_pending_post_reports(skip=0, limit=100)

        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].reason == "Inappropriate content"
        assert result[0].post_title == "Test Post"
        assert result[0].reporter_username == "reporter_user"
        moderator_service.post_repository.get_pending_post_reports.assert_called_once_with(
            0, 100
        )

    async def test_get_pending_post_reports_empty(self, moderator_service):
        """Test getting post reports when none exist."""
        moderator_service.post_repository.get_pending_post_reports.return_value = []

        result = await moderator_service.get_pending_post_reports(skip=0, limit=100)

        assert len(result) == 0

    async def test_get_pending_post_reports_pagination(
        self, moderator_service, test_post_report
    ):
        """Test getting post reports with pagination."""
        moderator_service.post_repository.get_pending_post_reports.return_value = [
            test_post_report
        ]

        result = await moderator_service.get_pending_post_reports(skip=50, limit=50)

        assert len(result) == 1
        moderator_service.post_repository.get_pending_post_reports.assert_called_once_with(
            50, 50
        )

    async def test_update_post_report_status_success(
        self, moderator_service, test_post_report
    ):
        """Test updating post report status successfully."""
        updated_report = MagicMock()
        updated_report.id = 1
        updated_report.user_id = 1
        updated_report.post_id = 1
        updated_report.reason = "Inappropriate content"
        # Create enum-like mock with value attribute
        status_mock = MagicMock()
        status_mock.value = "Reviewed"
        updated_report.status = status_mock
        updated_report.created_at = "2024-01-01T00:00:00"
        updated_report.reviewed_at = "2024-01-02T00:00:00"
        updated_report.post = test_post_report.post
        updated_report.user = test_post_report.user

        moderator_service.post_repository.get_pending_post_reports.return_value = [
            test_post_report
        ]
        moderator_service.post_repository.update_report_status.return_value = (
            updated_report
        )

        result = await moderator_service.update_post_report_status(
            report_id=1, status="Reviewed"
        )

        assert result.status == "Reviewed"
        assert result.id == 1
        moderator_service.post_repository.update_report_status.assert_called_once()

    async def test_update_post_report_status_not_found(self, moderator_service):
        """Test updating non-existent post report."""
        moderator_service.post_repository.get_pending_post_reports.return_value = []

        with pytest.raises(NotFoundException) as exc_info:
            await moderator_service.update_post_report_status(
                report_id=999, status="RESOLVED"
            )

        assert "Report with id 999 not found" in str(exc_info.value)

    async def test_get_pending_comment_reports_success(
        self, moderator_service, test_comment_report
    ):
        """Test getting pending comment reports successfully."""
        moderator_service.comment_repository.get_pending_comment_reports.return_value = [
            test_comment_report
        ]

        result = await moderator_service.get_pending_comment_reports(skip=0, limit=100)

        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].reason == "Spam"
        assert result[0].comment_title == "Test Comment"
        assert result[0].reporter_username == "reporter_user"
        moderator_service.comment_repository.get_pending_comment_reports.assert_called_once_with(
            0, 100
        )

    async def test_get_pending_comment_reports_empty(self, moderator_service):
        """Test getting comment reports when none exist."""
        moderator_service.comment_repository.get_pending_comment_reports.return_value = []

        result = await moderator_service.get_pending_comment_reports(skip=0, limit=100)

        assert len(result) == 0

    async def test_update_comment_report_status_success(
        self, moderator_service, test_comment_report
    ):
        """Test updating comment report status successfully."""
        updated_report = MagicMock()
        updated_report.id = 1
        updated_report.user_id = 1
        updated_report.comment_id = 1
        updated_report.reason = "Spam"
        updated_report.status = MagicMock()
        updated_report.status.value = "RESOLVED"
        updated_report.created_at = "2024-01-01T00:00:00"
        updated_report.reviewed_at = "2024-01-02T00:00:00"
        updated_report.comment = test_comment_report.comment
        updated_report.user = test_comment_report.user

        moderator_service.comment_repository.get_pending_comment_reports.return_value = [
            test_comment_report
        ]
        moderator_service.comment_repository.update_report_status.return_value = (
            updated_report
        )

        result = await moderator_service.update_comment_report_status(
            report_id=1, status="RESOLVED"
        )

        assert result.status == "RESOLVED"
        assert result.id == 1
        moderator_service.comment_repository.update_report_status.assert_called_once()

    async def test_update_comment_report_status_not_found(self, moderator_service):
        """Test updating non-existent comment report."""
        moderator_service.comment_repository.get_pending_comment_reports.return_value = []

        with pytest.raises(NotFoundException) as exc_info:
            await moderator_service.update_comment_report_status(
                report_id=999, status="RESOLVED"
            )

        assert "Report with id 999 not found" in str(exc_info.value)

    async def test_post_report_with_null_post(self, moderator_service):
        """Test post report when post has been deleted."""
        report = MagicMock()
        report.id = 1
        report.user_id = 1
        report.post_id = 1
        report.reason = "Inappropriate content"
        report.status = MagicMock()
        report.status.value = "PENDING"
        report.created_at = "2024-01-01T00:00:00"
        report.reviewed_at = None
        report.post = None
        report.user = MagicMock()
        report.user.username = "reporter_user"

        moderator_service.post_repository.get_pending_post_reports.return_value = [
            report
        ]

        result = await moderator_service.get_pending_post_reports(skip=0, limit=100)

        assert len(result) == 1
        assert result[0].post_title is None
        assert result[0].post_author_id is None

    async def test_comment_report_with_null_comment(self, moderator_service):
        """Test comment report when comment has been deleted."""
        report = MagicMock()
        report.id = 1
        report.user_id = 1
        report.comment_id = 1
        report.reason = "Spam"
        report.status = MagicMock()
        report.status.value = "PENDING"
        report.created_at = "2024-01-01T00:00:00"
        report.reviewed_at = None
        report.comment = None
        report.user = MagicMock()
        report.user.username = "reporter_user"

        moderator_service.comment_repository.get_pending_comment_reports.return_value = [
            report
        ]

        result = await moderator_service.get_pending_comment_reports(skip=0, limit=100)

        assert len(result) == 1
        assert result[0].comment_title is None
        assert result[0].comment_description is None

    async def test_report_with_null_user(self, moderator_service):
        """Test report when reporter user has been deleted."""
        report = MagicMock()
        report.id = 1
        report.user_id = 1
        report.post_id = 1
        report.reason = "Test reason"
        report.status = MagicMock()
        report.status.value = "PENDING"
        report.created_at = "2024-01-01T00:00:00"
        report.reviewed_at = None
        report.post = MagicMock()
        report.post.title = "Test Post"
        report.post.author_id = 2
        report.user = None

        moderator_service.post_repository.get_pending_post_reports.return_value = [
            report
        ]

        result = await moderator_service.get_pending_post_reports(skip=0, limit=100)

        assert len(result) == 1
        assert result[0].reporter_username is None
