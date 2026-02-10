"""add_deleted_status_to_report_enum

Revision ID: 9a772bc2538e
Revises: aa3c862be4e1
Create Date: 2026-02-10 18:08:03.678847

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9a772bc2538e"
down_revision: Union[str, Sequence[str], None] = "aa3c862be4e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if 'Deleted' already exists in the enum
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT 1 FROM pg_enum "
            "JOIN pg_type ON pg_enum.enumtypid = pg_type.oid "
            "WHERE pg_type.typname = 'reportstatus' AND enumlabel = 'Deleted'"
        )
    ).fetchone()

    # Only add if it doesn't exist
    if not result:
        # Note: ALTER TYPE ADD VALUE cannot be executed in a transaction block
        # So we need to close current transaction, add value, then start new one
        op.execute(sa.text("ALTER TYPE reportstatus ADD VALUE 'Deleted'"))


def downgrade() -> None:
    """Downgrade schema."""
    # Note: PostgreSQL doesn't support removing enum values directly
    # A full enum recreation would be needed, which is complex
    pass
