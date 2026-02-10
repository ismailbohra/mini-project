# app/posts/schema.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AuthorResponse(BaseModel):
    """Basic author information for responses."""
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


class TagResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    tags: List[str] = Field(..., min_items=0, max_items=10)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = Field(None, min_items=0, max_items=10)


class PostResponse(BaseModel):
    id: int
    author_id: int
    author: AuthorResponse
    title: str
    description: str
    tags: List[TagResponse]
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    user_has_liked: bool = False

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int


class PostLikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PostReportCreate(BaseModel):
    post_id: int
    reason: str = Field(..., min_length=1, max_length=500)


class PostReportResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    reason: str
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime]

    model_config = {"from_attributes": True}
