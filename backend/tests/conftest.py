"""
Pytest configuration and fixtures for testing.

This module provides fixtures for:
- SQLite test database
- Running Alembic migrations
- Test client for API testing
- Database sessions
"""

import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from app.config.database import get_session
from app.main import app
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Test database URL (SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
TEST_DATABASE_URL_SYNC = "sqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def setup_test_database():
    """
    Setup test database by creating tables from models.

    This fixture:
    1. Creates a SQLite test database
    2. Creates all tables from SQLAlchemy models (skips Alembic for SQLite compatibility)
    3. Yields control to tests
    4. Cleans up the database after all tests complete

    Note: We use direct table creation instead of Alembic migrations because
    SQLite doesn't support all PostgreSQL features used in migrations.
    """
    from app.config.database import Base
    from sqlalchemy import create_engine

    # Remove existing test database if it exists
    test_db_path = Path("./test.db")
    if test_db_path.exists():
        test_db_path.unlink()

    # Create tables synchronously using SQLite
    sync_engine = create_engine(
        TEST_DATABASE_URL_SYNC, connect_args={"check_same_thread": False}
    )

    # Create all tables from models
    Base.metadata.create_all(bind=sync_engine)

    yield

    # Cleanup: dispose engines and remove test database file.
    # Dispose the synchronous engine first.
    sync_engine.dispose()

    # Dispose the async test engine to close any open connections.
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_engine.dispose())
    except RuntimeError:
        # No running loop; create a temporary one to dispose the engine
        new_loop = asyncio.new_event_loop()
        try:
            new_loop.run_until_complete(test_engine.dispose())
        finally:
            new_loop.close()
    except Exception:
        # If dispose fails for any reason, continue to unlink retry below
        pass

    # Retry unlink for a short period (Windows may keep file handles briefly).
    import time

    max_wait = 5.0
    interval = 0.1
    waited = 0.0
    while test_db_path.exists() and waited < max_wait:
        try:
            test_db_path.unlink()
            break
        except PermissionError:
            time.sleep(interval)
            waited += interval
    # If still exists after retries, leave it (best-effort cleanup)


@pytest.fixture
async def db_session(setup_test_database) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for testing.

    Each test gets a fresh session that commits changes during the test
    but the session-scoped database is recreated between test runs.
    """
    async with TestSessionLocal() as session:
        yield session
        await session.close()


@pytest.fixture(autouse=True)
async def cleanup_database(setup_test_database):
    """
    Clear all tables after each test to ensure isolation.

    This fixture runs automatically after every test.
    """
    yield

    # Cleanup after test: truncate all tables
    from sqlalchemy import create_engine, text

    sync_engine = create_engine(
        TEST_DATABASE_URL_SYNC, connect_args={"check_same_thread": False}
    )

    with sync_engine.connect() as conn:
        # Get all table names
        from app.config.database import Base

        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"DELETE FROM {table.name}"))
            conn.commit()

    sync_engine.dispose()


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Override the get_session dependency for testing."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
async def client(setup_test_database) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async test client for API testing.

    This fixture:
    - Overrides the database session dependency to use test database
    - Provides an AsyncClient for making API requests
    - Cleans up after tests
    """
    # Override the database session dependency
    app.dependency_overrides[get_session] = override_get_session

    # Disable Redis caching for tests
    os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # Use test Redis DB

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/api"
    ) as ac:
        yield ac

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sync_client(setup_test_database) -> Generator[TestClient, None, None]:
    """
    Provide a synchronous test client for simple API testing.

    Useful for basic tests that don't require async context.
    """
    app.dependency_overrides[get_session] = override_get_session

    # Disable Redis caching for tests
    os.environ["REDIS_URL"] = "redis://localhost:6379/15"

    with TestClient(app, base_url="http://test/api") as client:
        yield client

    app.dependency_overrides.clear()
