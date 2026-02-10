# app/posts/schema.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


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
    title: str
    description: str
    tags: List[TagResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int