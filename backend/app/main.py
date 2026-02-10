from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.comments.model import Comment, CommentLike
from app.comments.router import router as comments_router
from app.posts.model import PostLike, Posts
from app.posts.router import router as posts_router
from app.users.model import User
from app.users.router import router as users_router

app = FastAPI(
    title="Mini Project API",
    description="Backend API for Mini Project",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(posts_router)
app.include_router(comments_router)
