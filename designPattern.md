# Design Patterns Analysis

This document provides a comprehensive evaluation of the design patterns implemented in the full-stack project (FastAPI + React).

## Backend Design Patterns (FastAPI)

### 1. Repository Pattern
- **Implementation**: Found in `app/*/repository.py` (e.g., `UserRepository`).
- **Description**: The codebase abstracts database operations into dedicated repository classes. These classes (`UserRepository`, `PostRepository`, etc.) handle all direct interactions with the database using SQLAlchemy.
- **Justification**: This decouples the business logic (Service Layer) from the data access layer. It makes the code more testable (mocking repositories is easier than mocking DB sessions) and allows swapping the database implementation with minimal impact on business logic.
- **Evaluation**: The implementation is clean and follows standard practices. It correctly implements interfaces (`UserRepositoryInterface`) which further enhances loose coupling.

### 2. Service Layer Pattern
- **Implementation**: Found in `app/*/service.py` (e.g., `UserService`).
- **Description**: Service classes encapsulate the business logic of the application. They call the repository layer for data and perform operations like validation, caching checks, and external service calls.
- **Justification**: This ensures "Separation of Concerns". The routers (controllers) handle HTTP requests, while services handle the domain logic. This prevents "fat controllers" and promotes code reuse.
- **Evaluation**: The usage of `UserService` to handle caching (Redis) before hitting the repository is a great example of this pattern's utility.

### 3. Dependency Injection (DI)
- **Implementation**: Heavily used in `app/*/router.py` and `app/*/dependency.py` via FastAPI's `Depends`.
- **Description**: Dependencies like database sessions, current user, and service instances are "injected" into route handlers rather than being instantiated inside them.
- **Justification**: DI improves modularity and testability. It allows the framework (FastAPI) to manage the lifecycle of resources (opening/closing DB sessions).
- **Evaluation**: effectively used. The chain of dependencies (`get_session` -> `UserRepository` -> `UserService` -> Router) is a textbook example of Inversion of Control in FastAPI.

### 4. Singleton Pattern
- **Implementation**: 
    - `app/config/database.py`: The `engine` and `AsyncSessionLocal` are created once and reused.
    - `app/utils/redis.py`: The Redis client is initialized as a module-level singleton.
- **Description**: Ensures a class or resource has only one instance and provides a global point of access to it.
- **Justification**: Essential for resource-heavy objects like database connection pools and Redis clients. Creating a new connection for every request would be inefficient.
- **Evaluation**: Correctly implemented using Python's module-level scope capabilities.

### 5. Middleware / Chain of Responsibility
- **Implementation**: `app/middleware/role_verification.py`.
- **Description**: The `RoleVerificationMiddleware` sits between the client and the main application logic. It processes requests (verifying user roles) before they reach the endpoint.
- **Justification**: Perfect for cross-cutting concerns like authentication, logging, and CORS. It keeps these concerns out of the core business logic.
- **Evaluation**: The implementation inherits from `BaseHTTPMiddleware`, which is the standard way to add middleware in Starlette/FastAPI.

### 6. Observer Pattern (Pub/Sub)
- **Implementation**: `app/websocket/manager.py` (WebSocketManager).
- **Description**: The `WebSocketManager` maintains a list of active connections (observers). When an event occurs (like a notification), it iterates through relevant connections and sends updates.
- **Justification**: specific for real-time features. It allows the server to push updates to clients without them polling.
- **Evaluation**: The manager handles connection lifecycle (connect/disconnect) and broadcasting.

---

## Frontend Design Patterns (React)

### 1. Component-Based Architecture / Composite Pattern
- **Implementation**: `Frontend/src/components/`, `Frontend/src/pages/`.
- **Description**: The UI is built from small, reusable components (`PostCard`, `Header`) that are composed together to form complex pages.
- **Justification**: Core to React. It promotes reusability, maintainability, and testing of individual UI parts.
- **Evaluation**: The structure distinguishes between reusable `components` and page-level `pages`, which is a good practice.

### 2. Service Module Pattern / Facade
- **Implementation**: `Frontend/src/services/api.js`.
- **Description**: The `api` module acts as a facade over the Axios library. It creates a centralized instance with base URLs, interceptors for auth tokens, and global error handling.
- **Justification**: Prevents code duplication. If the API URL changes or you need to add a header to every request, you only change it in one place.
- **Evaluation**: The interceptors for handling 401 errors and attaching tokens are well-implemented.

### 3. State Management (Flux-like / Singleton Store)
- **Implementation**: `Frontend/src/store/index.js` (Redux Toolkit).
- **Description**: Application state is kept in a single valid store. Changes trigger UI updates.
- **Justification**: Essential for complex applications where multiple components need access to the same data (e.g., user profile, notifications) without prop drilling.
- **Evaluation**: using Redux Toolkit slices (`authSlice`, `postSlice`) organizes state logic efficiently.

### 4. Custom Hooks Pattern
- **Implementation**: `Frontend/src/hooks/` (e.g., `useMentionAutocomplete.js`).
- **Description**: Encapsulates stateful logic (like managing mention suggestions) so it can be reused across different components.
- **Justification**: Promotes code reuse and cleaner components. It separates logic from the view.
- **Evaluation**: `useMentionAutocomplete` likely handles the complex logic of fetching users based on keystrokes, keeping the input component clean.

### 5. Higher-Order Component (HOC) / Wrapper Pattern
- **Implementation**: `ProtectedRoute.jsx`.
- **Description**: A wrapper component that checks if a user is authenticated before rendering the child component (the actual route).
- **Justification**: Standard pattern for route protection in React. It centralizes auth logic.
- **Evaluation**: Simple and effective way to guard routes.
