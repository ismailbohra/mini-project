"""
Test package initialization.

Sets up environment variables for testing before any imports.
This ensures that tests always use SQLite instead of PostgreSQL.
"""

import os

# Set test environment variables before any app imports
# This ensures SQLite is used for testing, not PostgreSQL
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["DATABASE_URL_SYNC"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_USER"] = "test"
os.environ["POSTGRES_PASSWORD"] = "test"
os.environ["POSTGRES_DB"] = "test_db"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_DB"] = "15"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
