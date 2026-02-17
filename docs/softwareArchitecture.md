The following files were successfully edited:# Software Architecture Analysis

c:\Ismail Bohra\Mini-Project\softwareArchitecture.md
This document analyzes the architectural style and structural decisions of the project.

## 1. Architectural Style

The project follows a **Layered Architecture** within a **Client-Server** model, enhanced with **Event-Driven** elements.

-   **Layered Monolith (Backend)**: The backend is structured into distinct horizontal layers (Presentation/Router, Business/Service, Data Access/Repository) and vertical feature modules (Auth, Users, Posts, etc.). This makes it a "Modular Monolith".
-   **Client-Server**: The implementation completely decouples the frontend (React/Vite) from the backend (FastAPI). Communication happens strictly over HTTP (REST) and WebSocket.
-   **Event-Driven Extensions**: The system uses a Redis-backed Event Bus to handle side effects (like notifications) asynchronously, moving towards an event-driven design without the full complexity of microservices.

## 2. Responsibility Division

### API Routes (Presentation Layer)
-   **Role**: Entry point for HTTP requests.
-   **Responsibilities**:
    -   Defining path operations and HTTP methods.
    -   Validating inputs using Pydantic schemas.
    -   Resolving dependencies (Database, Services, Current User).
    -   Returning HTTP responses/status codes.
-   **Example**: `app/users/router.py` receives a user creation request, validates the `UserCreate` schema, and passes it to `UserService`.

### Business Logic (Service Layer)
-   **Role**: The brain of the application.
-   **Responsibilities**:
    -   Orchestrating workflows (e.g., "Create user" -> "Hash password" -> "Save to DB").
    -   **Caching**: deciding when to read from Redis vs. SQL.
    -   **Events**: Publishing events (e.g., `post.liked`) to the Event Bus.
    -   Enforcing business rules (e.g., "Parent comment must belong to the same post").
-   **Example**: `CommentService` checks if a parent comment exists and belongs to the correct post before allowing a reply.

### Persistence Layer (Repository Pattern)
-   **Role**: Abstraction over the database.
-   **Responsibilities**:
    -   Constructing and executing raw SQL or ORM queries.
    -   Mapping database rows to Python objects.
    -   Handling database transaction commits/rollbacks (via session management).
-   **Example**: `UserRepository` executes `select(User).where(User.email == email)`.

### Caching Layer (Redis)
-   **Role**: Performance optimization for read-heavy data.
-   **Implementation**: A custom wrapper `app/utils/redis.py` (and `redis_cache.py`) abstracts the Redis client.
-   **Usage**:
    -   User profiles (`user:profile:{id}`) validation.
    -   Unread notification counts (`notifications:unread:{id}`).
-   **Invalidation**: Handled explicitly in services. For example, `NotificationService.mark_as_read` deletes the unread count cache key.

### Messaging (Redis Pub/Sub)
-   **Role**: Asynchronous communication.
-   **Implementation**: `app/utils/event_bus.py` provides a `RedisEventBus`.
-   **Usage**:
    -   **Publishing**: When a user likes a post, `PostService` publishes a `post.liked` event.
    -   **Subscribing**: Background listeners (likely started in `main.py`) receive these events and trigger actions like creating a notification record.
    -   **WebSockets**: The `WebSocketManager` likely subscribes to user-specific channels to push real-time updates to the frontend.

## 3. SQLAlchemy ORM Usage

The project uses modern **SQLAlchemy 2.0+ (AsyncIO)** features:
-   **Domain Models**: Defined in `model.py` classes (e.g., `Posts`, `Users`) inheriting from `Base`. They use mapped attributes (`Mapped[int]`) for type hinting.
-   **Persistence**:
    -   **AsyncSession**: API routes allow `await session.commit()`, preventing the thread from blocking during database I/O.
    -   **Relationships**: `relationship()` is used to define links (e.g., `User.posts`), allowing simple traversal, though care must be taken with async loading (lazy loading doesn't work well in async without explicit handling).
    -   **Query Construction**: Uses the fluent `select()` syntax, which is the preferred modern method over the legacy `Query` object.

## 4. Architectural Evaluation

### Scalability: **High**
-   **Async I/O**: FastAPI + Async SQLAlchemy allows the single process to handle thousands of concurrent connections (waiting for DB/Redis) without blocking.
-   **Stateless API**: No session affinity is required; JWTs are self-contained.
-   **Read Scaling**: Redis offloads common read operations (user profiles, counts) from the primary database.

### Testability: **High**
-   **Dependency Injection**: The pervasive use of `Depends()` and the separation of Repositories means you can easily inject `MockRepository` or `MockService` during unit tests.
-   **Separation**: You can test business logic (Services) without spinning up a real HTTP server.

### Maintainability: **Medium-High**
-   **Modularity**: Packaging code by feature (`users`, `posts`, `auth`) rather than by type (`/controllers`, `/models`) makes it easier to navigate the codebase.
-   **Boilerplate**: The Repository/Service pattern adds somewhat code volume, which needs to be maintained, but the clarity it provides is worth it.

### Fault Tolerance: **Medium**
-   **Error Handling**: Global exception handlers in `app/utils/exceptions.py` ensure the API returns clean JSON errors instead of crashing.
-   **Redis Resilience**: The `RedisCache` wrapper catches exceptions (`try...except`). If Redis goes down, `get_cache` returns `None`, and the system transparently falls back to the database. This is a robust "Fail-Open" design.
