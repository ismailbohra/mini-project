# app/comments/schema.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AuthorResponse(BaseModel):
    """Basic author information for responses."""

    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    post_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    parent_comment_id: Optional[int] = None


class CommentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)


class CommentResponse(BaseModel):
    id: int
    author_id: int
    author: AuthorResponse
    post_id: int
    title: str
    description: str
    parent_comment_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    user_has_liked: bool = False
    replies: List["CommentResponse"] = []

    model_config = {"from_attributes": True}


class CommentLikeResponse(BaseModel):
    id: int
    user_id: int
    comment_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentReportCreate(BaseModel):
    comment_id: int
    reason: str = Field(..., min_length=1, max_length=500)


class CommentReportResponse(BaseModel):
    id: int
    user_id: int
    comment_id: int
    reason: str
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime]
    # Enriched fields
    comment_title: Optional[str] = None
    comment_description: Optional[str] = None
    comment_author_id: Optional[int] = None
    comment_author_username: Optional[str] = None
    reporter_username: Optional[str] = None

    model_config = {"from_attributes": True}
