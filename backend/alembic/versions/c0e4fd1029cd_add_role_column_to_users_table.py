"""add_role_column_to_users_table

Revision ID: c0e4fd1029cd
Revises: 97057f07dc6e
Create Date: 2026-02-10 09:56:25.953356

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c0e4fd1029cd"
down_revision: Union[str, Sequence[str], None] = "97057f07dc6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add role column to users table with default 'USER' (uppercase to match existing enum)
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("ADMIN", "USER", "MODERATOR", name="roletype", create_type=False),
            nullable=False,
            server_default="USER",
        ),
    )

    # Migrate data from user_roles to users table if the table exists (take the most recent role for each user)
    connection = op.get_bind()
    if connection.dialect.has_table(connection, "user_roles"):
        op.execute("""
            UPDATE users
            SET role = (
                SELECT role FROM user_roles 
                WHERE user_roles.user_id = users.id 
                ORDER BY user_roles.assigned_at DESC 
                LIMIT 1
            )
            WHERE EXISTS (
                SELECT 1 FROM user_roles WHERE user_roles.user_id = users.id
            )
        """)

        # Drop the user_roles table
        op.drop_table("user_roles")


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate user_roles table
    op.create_table(
        "user_roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "USER", "MODERATOR", name="roletype", create_type=False),
            nullable=False,
        ),
        sa.Column("assigned_by", sa.Integer(), nullable=True),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"]),
    )

    # Migrate data back from users to user_roles
    op.execute("""
        INSERT INTO user_roles (user_id, role, assigned_by, assigned_at)
        SELECT id, role, NULL, created_at FROM users
    """)

    # Drop role column from users
    op.drop_column("users", "role")
