# app/comments/schema.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


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
    post_id: int
    title: str
    description: str
    parent_comment_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    replies: List["CommentResponse"] = []

    model_config = {"from_attributes": True}


class CommentLikeResponse(BaseModel):
    id: int
    user_id: int
    comment_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
