from datetime import datetime
from enum import Enum as PyEnum

from app.config.database import Base
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ReportStatus(PyEnum):
    """Status of a report."""

    PENDING = "Pending"
    REVIEWED = "Reviewed"
    DELETED = "Deleted"


class Posts(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    image_path: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("PostLike", back_populates="post")
    tags = relationship("PostTag", back_populates="post")
    mentions = relationship(
        "PostMention", back_populates="post", cascade="all, delete-orphan"
    )


class Tags(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)

    posts = relationship("PostTag", back_populates="tag")


class PostTag(Base):
    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    post = relationship("Posts", back_populates="tags")
    tag = relationship("Tags", back_populates="posts")


class PostLike(Base):
    __tablename__ = "post_likes"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="unique_post_like"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="post_likes")
    post = relationship("Posts", back_populates="likes")


class PostReport(Base):
    __tablename__ = "post_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    reason: Mapped[str] = mapped_column(String)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, values_callable=lambda x: [e.value for e in x]),
        default=ReportStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user = relationship("User")
    post = relationship("Posts")


class PostMention(Base):
    __tablename__ = "post_mentions"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"), primary_key=True, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    post = relationship("Posts", back_populates="mentions")
    user = relationship("User", back_populates="post_mentions")
