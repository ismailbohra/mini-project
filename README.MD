# Social Media Platform - Mini Project

A full-stack social media platform built with FastAPI (backend) and React (frontend), featuring real-time notifications, role-based access control, and comprehensive moderation capabilities.

## 🏗️ Architecture

### Tech Stack

**Backend:**
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL 15
- **Cache & Message Broker**: Redis 7
- **ORM**: SQLAlchemy
- **Migration**: Alembic
- **Authentication**: JWT-based

**Frontend:**
- **Framework**: React 19 with Vite
- **State Management**: Redux Toolkit
- **UI Library**: React Bootstrap
- **Routing**: React Router DOM
- **HTTP Client**: Axios

**Infrastructure:**
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (for frontend)
- **Real-time Communication**: WebSocket

### System Components

```
┌─────────────┐
│   Frontend  │ (React + Nginx)
│   Port: 80  │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────┐     ┌──────────┐
│   Backend   │────▶│PostgreSQL│     │  Redis   │
│   Port:8000 │     │Port: 5432│◀────│Port: 6379│
└─────────────┘     └──────────┘     └──────────┘
       │                                    ▲
       │                                    │
       └────────────────────────────────────┘
           Event Bus & Caching
```

### Key Features
- **Role-Based Access Control (RBAC)**: Admin, Moderator, and User roles
- **Real-time Notifications**: WebSocket-based notification system
- **Event-Driven Architecture**: Redis pub/sub for inter-component communication
- **Caching Strategy**: Redis caching with cache hit/miss headers
- **File Upload**: Support for profile images and post images
- **Soft Delete**: Logical deletion for posts and comments
- **Mentions System**: User mentions in posts and comments

---

## 📊 Database Schema

### Core Tables

#### **Users**
```sql
- id (PK)
- username (unique, indexed)
- email (unique, indexed)
- hashed_password
- role (Admin/User/Moderator)
- is_active (boolean)
- is_deleted (boolean)
- profile_image (nullable)
- created_at, updated_at
```

#### **Posts**
```sql
- id (PK)
- author_id (FK -> users.id, indexed)
- title (indexed)
- description
- image_path (nullable)
- is_deleted (boolean)
- created_at, updated_at

Relations:
  - author (User)
  - comments (Comments[])
  - likes (PostLike[])
  - tags (PostTag[])
  - mentions (PostMention[])
```

#### **Comments**
```sql
- id (PK)
- author_id (FK -> users.id, indexed)
- post_id (FK -> posts.id, indexed)
- parent_comment_id (FK -> comments.id, nullable, indexed) # For nested replies
- title (indexed)
- description
- is_deleted (boolean)
- created_at, updated_at

Relations:
  - author (User)
  - post (Posts)
  - parent (Comment)
  - replies (Comment[])
  - likes (CommentLike[])
  - mentions (CommentMention[])
```

#### **Tags**
```sql
- id (PK)
- name (unique, indexed)

Relations:
  - posts (PostTag[])
```

#### **PostTag** (Many-to-Many)
```sql
- post_id (PK, FK -> posts.id)
- tag_id (PK, FK -> tags.id)
```

#### **PostLike**
```sql
- id (PK)
- user_id (FK -> users.id, indexed)
- post_id (FK -> posts.id, indexed)
- created_at
Unique Constraint: (user_id, post_id)
```

#### **CommentLike**
```sql
- id (PK)
- user_id (FK -> users.id, indexed)
- comment_id (FK -> comments.id, indexed)
- created_at
Unique Constraint: (user_id, comment_id)
```

#### **PostMention**
```sql
- post_id (PK, FK -> posts.id, indexed)
- user_id (PK, FK -> users.id, indexed)
- created_at
```

#### **CommentMention**
```sql
- comment_id (PK, FK -> comments.id, indexed)
- user_id (PK, FK -> users.id, indexed)
- post_id (FK -> posts.id, indexed)
- created_at
```

#### **PostReport**
```sql
- id (PK)
- user_id (FK -> users.id, indexed)
- post_id (FK -> posts.id, indexed)
- reason
- status (Pending/Reviewed/Deleted)
- created_at, reviewed_at
```

#### **CommentReport**
```sql
- id (PK)
- user_id (FK -> users.id, indexed)
- comment_id (FK -> comments.id, indexed)
- reason
- status (Pending/Reviewed/Deleted)
- created_at, reviewed_at
```

#### **Notifications**
```sql
- id (PK)
- receiver_id (FK -> users.id, indexed)
- actor_id (FK -> users.id, indexed)
- type (indexed)
- post_id (FK -> posts.id, nullable, indexed)
- comment_id (FK -> comments.id, nullable, indexed)
- is_read (boolean, indexed)
- created_at
```

---

## 🚀 API Endpoints

### Authentication (`/api/auth`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login` | User login, returns JWT token | ❌ |
| POST | `/auth/change-password` | Change user password | ✅ |

### Users (`/api/users`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/users/me` | Get current user info | ✅ |
| POST | `/users` | Register new user (with optional profile image) | ❌ |
| PUT | `/users` | Update user profile | ✅ |
| GET | `/users/search/mentions` | Search users for @mentions | ✅ |

### Posts (`/api/posts`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/posts` | Get all posts (search, filter, sort) | ❌ |
| GET | `/posts/{post_id}` | Get single post by ID | ❌ |
| GET | `/posts/user/me` | Get current user's posts | ✅ |
| POST | `/posts` | Create new post (with optional image) | ✅ |
| PUT | `/posts/{post_id}` | Update post (Owner/Admin/Mod) | ✅ |
| DELETE | `/posts/{post_id}` | Delete post (Owner/Admin/Mod) | ✅ |
| GET | `/posts/tags` | Get all tags | ❌ |
| GET | `/posts/search/suggestions` | Get search suggestions | ❌ |
| POST | `/posts/{post_id}/like` | Like a post | ✅ |
| DELETE | `/posts/{post_id}/like` | Unlike a post | ✅ |
| GET | `/posts/{post_id}/likes/count` | Get post likes count | ❌ |
| POST | `/posts/{post_id}/report` | Report a post | ✅ |

### Comments (`/api/comments`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/comments/post/{post_id}` | Get all comments for a post | ❌ |
| POST | `/comments` | Create comment or reply | ✅ |
| PUT | `/comments/{comment_id}` | Update comment (Owner/Admin/Mod) | ✅ |
| DELETE | `/comments/{comment_id}` | Delete comment (Owner/Admin/Mod) | ✅ |
| POST | `/comments/{comment_id}/like` | Like a comment | ✅ |
| DELETE | `/comments/{comment_id}/like` | Unlike a comment | ✅ |
| POST | `/comments/{comment_id}/report` | Report a comment | ✅ |

### Admin (`/api/admin`) - Admin Only
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/admin/assign-role` | Assign role to user | ✅ Admin |
| GET | `/admin/users` | Get all users with pagination | ✅ Admin |
| PATCH | `/admin/users/{user_id}/toggle` | Toggle user active status | ✅ Admin |
| GET | `/admin/dashboard/analytics` | Get dashboard analytics | ✅ Admin |

### Moderator (`/api/moderator`) - Moderator Only
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/moderator/reports/posts` | Get all post reports | ✅ Mod |
| PUT | `/moderator/reports/posts/{report_id}/status` | Update post report status | ✅ Mod |
| GET | `/moderator/reports/comments` | Get all comment reports | ✅ Mod |
| PUT | `/moderator/reports/comments/{report_id}/status` | Update comment report status | ✅ Mod |

### Notifications (`/api/notifications`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/notifications` | Get user notifications | ✅ |
| GET | `/notifications/unread/count` | Get unread notification count | ✅ |
| PATCH | `/notifications/{notification_id}/read` | Mark notification as read | ✅ |
| PATCH | `/notifications/read-all` | Mark all notifications as read | ✅ |
| WS | `/notifications/ws` | WebSocket for real-time notifications | ✅ |

### Health Check
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | API health check | ❌ |

### Static Assets
| Path | Description |
|------|-------------|
| `/assets/users/*` | User profile images |
| `/assets/posts/*` | Post images |

---

## 🔄 User Flow

### 1. **Registration & Authentication**
```
User Registration → Email Verification → Login → JWT Token Received
                                                          ↓
                                              Stored in Redux + LocalStorage
```

### 2. **Normal User Journey**
```
Home Page (View Posts)
    ↓
    ├─→ Search/Filter Posts (by title, tags, author)
    ├─→ View Post Details
    │       ├─→ Like/Unlike Post
    │       ├─→ Add Comment
    │       ├─→ Like/Unlike Comment
    │       ├─→ Reply to Comment (nested)
    │       ├─→ Mention Users (@username)
    │       └─→ Report Post/Comment
    ├─→ Create New Post (with image & tags)
    ├─→ My Posts (Edit/Delete own posts)
    ├─→ Notifications (Real-time via WebSocket)
    └─→ Profile Management (Update profile image)
```

### 3. **Moderator Journey**
```
All User Features
    +
Review Dashboard
    ├─→ View Post Reports
    ├─→ View Comment Reports
    ├─→ Update Report Status (Reviewed/Deleted)
    └─→ Delete/Edit any Post/Comment
```

### 4. **Admin Journey**
```
All Moderator Features
    +
Admin Dashboard
    ├─→ View All Users
    ├─→ Assign Roles (Admin/Moderator/User)
    ├─→ Activate/Deactivate Users
    └─→ View Analytics
            ├─→ User Statistics (Total, by role, active)
            ├─→ Post Statistics
            ├─→ Top Mentioned Users
            ├─→ Top Tags
            └─→ Top Reported Users
```

### 5. **Real-time Notifications Flow**
```
Event Occurs (Like, Comment, Mention, Report)
    ↓
Redis Event Bus (Pub/Sub)
    ↓
Notification Created in DB
    ↓
WebSocket Push to Connected Users
    ↓
Frontend Updates Notification Badge in Real-time
```

---

## 🛠️ Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone <repository-url>
cd Mini-Project
```

2. **Set up environment variables**
Create `.env` file in `backend/` directory:
```env
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. **Build and run with Docker Compose**
```bash
# Build and start all services
docker compose up -d --build

# Check service status
docker compose ps

# View logs
docker compose logs -f
```

4. **Run database migrations**
```bash
# Enter backend container
docker compose exec backend bash

# Run migrations
alembic upgrade head

# Exit container
exit
```

5. **Access the application**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Local Development Setup

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd Frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 📝 Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "description_of_changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

---

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

---

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for password security
- **Role-Based Access Control**: Fine-grained permission system
- **CORS Configuration**: Controlled cross-origin requests
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
- **File Upload Validation**: Restricted file types and sizes

---

## 🚦 Performance Optimizations

- **Redis Caching**: Frequently accessed data cached with TTL
- **Cache Headers**: `X-Cache: HIT/MISS` headers for monitoring
- **Database Indexing**: Strategic indexes on frequently queried columns
- **Lazy Loading**: Relationships loaded on demand
- **WebSocket**: Real-time updates without polling
- **Static File Serving**: Nginx for efficient asset delivery
- **Connection Pooling**: PostgreSQL connection pooling via SQLAlchemy

---

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🐛 Known Issues & Future Enhancements

### Future Features
- [ ] Email notifications
- [ ] Password reset functionality
- [ ] User blocking/following system
- [ ] Advanced search with Elasticsearch
- [ ] Rate limiting per user
- [ ] Media compression for uploads
- [ ] Dark mode support
- [ ] Mobile responsive improvements

---

## 📞 Support

For issues and questions, please open an issue in the GitHub repository.