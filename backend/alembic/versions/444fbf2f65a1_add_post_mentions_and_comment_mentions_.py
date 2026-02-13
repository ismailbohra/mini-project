"""add_post_mentions_and_comment_mentions_tables

Revision ID: 444fbf2f65a1
Revises: d3afb3821d05
Create Date: 2026-02-12 18:04:58.362967

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "444fbf2f65a1"
down_revision: Union[str, Sequence[str], None] = "d3afb3821d05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create post_mentions table
    op.create_table(
        "post_mentions",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("post_id", "user_id"),
    )
    op.create_index(
        op.f("ix_post_mentions_post_id"), "post_mentions", ["post_id"], unique=False
    )
    op.create_index(
        op.f("ix_post_mentions_user_id"), "post_mentions", ["user_id"], unique=False
    )

    # Create comment_mentions table
    op.create_table(
        "comment_mentions",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("comment_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("comment_id", "user_id"),
    )
    op.create_index(
        op.f("ix_comment_mentions_comment_id"),
        "comment_mentions",
        ["comment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_comment_mentions_post_id"),
        "comment_mentions",
        ["post_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_comment_mentions_user_id"),
        "comment_mentions",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_comment_mentions_user_id"), table_name="comment_mentions")
    op.drop_index(op.f("ix_comment_mentions_post_id"), table_name="comment_mentions")
    op.drop_index(op.f("ix_comment_mentions_comment_id"), table_name="comment_mentions")
    op.drop_table("comment_mentions")

    op.drop_index(op.f("ix_post_mentions_user_id"), table_name="post_mentions")
    op.drop_index(op.f("ix_post_mentions_post_id"), table_name="post_mentions")
    op.drop_table("post_mentions")
