"""Add allergy to users.

Revision ID: 0003_add_user_allergy
Revises: 0002_add_user_profile_goals
Create Date: 2026-08-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_add_user_allergy"
down_revision = "0002_add_user_profile_goals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("allergy", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "allergy")
