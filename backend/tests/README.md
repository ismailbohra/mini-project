# Backend Tests

This directory contains the test suite for the backend application.

## Database Configuration

### Testing (SQLite)
Tests use **SQLite** for speed and isolation:
- Database: `sqlite+aiosqlite:///./test.db`
- No external dependencies required
- Automatically created and cleaned up
- Each test runs in isolation

### Production (PostgreSQL)
Production uses **PostgreSQL**:
- Configured via environment variables in `.env`
- Runs in Docker container
- Persistent data storage

The test configuration automatically switches to SQLite when running tests, ensuring your production database is never affected.

## Test Structure

- **`conftest.py`**: Pytest configuration and fixtures
  - SQLite test database setup
  - Alembic migration runner
  - Test client fixtures
  - Session management

- **`test_auth.py`**: Unit tests for authentication module
  - Login functionality
  - Password change
  - Token generation
  - User authentication

- **`test_users.py`**: Unit tests for user management module
  - User creation
  - User retrieval
  - User updates
  - Username validation
  - Pagination

- **`test_integration_auth_user.py`**: End-to-end integration tests
  - Complete authentication flow
  - User registration and login
  - Protected endpoint access
  - Password change workflow

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
# Run auth tests only
pytest tests/test_auth.py

# Run user tests only
pytest tests/test_users.py

# Run integration tests only
pytest tests/test_integration_auth_user.py
```

### Run Tests by Marker

```bash
# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run end-to-end tests only
pytest -m e2e
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

## Test Database

- Tests use **SQLite** (`test.db`) instead of PostgreSQL for faster execution and isolation
- Database is created at `./test.db` in the backend directory
- Tables are created directly from SQLAlchemy models (not via Alembic migrations)
- Each test gets isolated data - tables are cleared automatically after each test
- Database is automatically cleaned up after test session completes
- **Redis is mocked** to prevent actual connections during tests

**Important**: The test configuration (`tests/__init__.py` and `conftest.py`) automatically 
sets environment variables to use SQLite. This ensures your **production PostgreSQL database 
is never touched** during testing.

**Note**: We use direct table creation (`Base.metadata.create_all()`) instead of 
Alembic migrations because SQLite doesn't support all PostgreSQL-specific features 
used in the migrations (like `pg_enum` or certain ALTER TABLE operations).

## Test Fixtures

### Database Fixtures

- **`setup_test_database`**: Session-scoped fixture that creates and migrates the test database
- **`db_session`**: Function-scoped fixture providing a database session for each test

### API Fixtures

- **`client`**: Async HTTP client for testing API endpoints
- **`sync_client`**: Synchronous HTTP client for simple tests

### User Fixtures

- **`test_user`**: Creates an active test user
- **`inactive_user`**: Creates an inactive test user
- **`existing_user`**: Creates an existing user for duplicate tests
- **`multiple_users`**: Creates multiple users for pagination tests

## Test Markers

- `@pytest.mark.unit`: Unit tests (isolated components)
- `@pytest.mark.integration`: Integration tests (multiple components)
- `@pytest.mark.e2e`: End-to-end tests (complete workflows)

## Notes

- **Tests use SQLite**, production uses PostgreSQL - they are completely isolated
- **Redis is mocked** during tests using `unittest.mock` to prevent actual connections
- Redis would use database 15 if it were to connect, to avoid conflicts with production (db 0)
- Tests are fully isolated and **never affect production data**
- Each test gets a fresh database session
- Test database schema is created directly from models, ensuring it matches the application structure
