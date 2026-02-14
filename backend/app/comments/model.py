from datetime import datetime
from typing import Optional

from app.config.database import Base
from app.posts.model import ReportStatus
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


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_comment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id"), index=True, nullable=True
    )

    author = relationship("User", back_populates="comments")
    post = relationship("Posts", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="parent")
    likes = relationship("CommentLike", back_populates="comment")
    mentions = relationship(
        "CommentMention", back_populates="comment", cascade="all, delete-orphan"
    )


class CommentLike(Base):
    __tablename__ = "comment_likes"
    __table_args__ = (
        UniqueConstraint("user_id", "comment_id", name="unique_comment_like"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="comment_likes")
    comment = relationship("Comment", back_populates="likes")


class CommentReport(Base):
    __tablename__ = "comment_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), index=True)
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
    comment = relationship("Comment")


class CommentMention(Base):
    __tablename__ = "comment_mentions"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id"), primary_key=True, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    comment = relationship("Comment", back_populates="mentions")
    user = relationship("User", back_populates="comment_mentions")
    post = relationship("Posts")
