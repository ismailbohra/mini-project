"""add notifications table

Revision ID: f7e3b9d84a2c
Revises: 9a772bc2538e
Create Date: 2026-02-11 11:36:25.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f7e3b9d84a2c"
down_revision: Union[str, Sequence[str], None] = "9a772bc2538e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("receiver_id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.Column("comment_id", sa.Integer(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["receiver_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["posts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["comment_id"],
            ["comments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(
        op.f("ix_notifications_receiver_id"),
        "notifications",
        ["receiver_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_actor_id"), "notifications", ["actor_id"], unique=False
    )
    op.create_index(
        op.f("ix_notifications_type"), "notifications", ["type"], unique=False
    )
    op.create_index(
        op.f("ix_notifications_post_id"), "notifications", ["post_id"], unique=False
    )
    op.create_index(
        op.f("ix_notifications_comment_id"),
        "notifications",
        ["comment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_is_read"), "notifications", ["is_read"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_notifications_is_read"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_comment_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_post_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_actor_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_receiver_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")
