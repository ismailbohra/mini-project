"""add_report_tables

Revision ID: 061eb8127d4c
Revises: 5c0363c944fb
Create Date: 2026-02-10 12:08:04.452634

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '061eb8127d4c'
down_revision: Union[str, Sequence[str], None] = '5c0363c944fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type for report status (if not exists)
    report_status_enum = postgresql.ENUM('Pending', 'Reviewed', 'Dismissed', name='reportstatus', create_type=False)
    report_status_enum.create(op.get_bind(), checkfirst=True)

    # Create post_reports table
    op.create_table(
        'post_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('status', postgresql.ENUM('Pending', 'Reviewed', 'Dismissed', name='reportstatus', create_type=False), nullable=False, server_default='Pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_reports_id'), 'post_reports', ['id'], unique=False)
    op.create_index(op.f('ix_post_reports_post_id'), 'post_reports', ['post_id'], unique=False)
    op.create_index(op.f('ix_post_reports_user_id'), 'post_reports', ['user_id'], unique=False)

    # Create comment_reports table
    op.create_table(
        'comment_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('status', postgresql.ENUM('Pending', 'Reviewed', 'Dismissed', name='reportstatus', create_type=False), nullable=False, server_default='Pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comment_reports_comment_id'), 'comment_reports', ['comment_id'], unique=False)
    op.create_index(op.f('ix_comment_reports_id'), 'comment_reports', ['id'], unique=False)
    op.create_index(op.f('ix_comment_reports_user_id'), 'comment_reports', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop comment_reports table
    op.drop_index(op.f('ix_comment_reports_user_id'), table_name='comment_reports')
    op.drop_index(op.f('ix_comment_reports_id'), table_name='comment_reports')
    op.drop_index(op.f('ix_comment_reports_comment_id'), table_name='comment_reports')
    op.drop_table('comment_reports')

    # Drop post_reports table
    op.drop_index(op.f('ix_post_reports_user_id'), table_name='post_reports')
    op.drop_index(op.f('ix_post_reports_post_id'), table_name='post_reports')
    op.drop_index(op.f('ix_post_reports_id'), table_name='post_reports')
    op.drop_table('post_reports')

    # Drop enum type
    op.execute('DROP TYPE reportstatus')
