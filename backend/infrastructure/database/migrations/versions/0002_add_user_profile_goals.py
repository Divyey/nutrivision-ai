"""Add profile and goal columns to users.

Revision ID: 0002_add_user_profile_goals
Revises: 0001_create_users
Create Date: 2026-08-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_user_profile_goals"
down_revision = "0001_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("gender", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("weight_kg", sa.Numeric(6, 2), nullable=True))
    op.add_column("users", sa.Column("height_cm", sa.Numeric(6, 2), nullable=True))
    op.add_column("users", sa.Column("activity_level", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("vegan_status", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("status", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("start_date", sa.Date(), nullable=True))
    op.add_column("users", sa.Column("target_calories", sa.Numeric(10, 2), nullable=True))
    op.add_column("users", sa.Column("target_protein", sa.Numeric(10, 2), nullable=True))
    op.add_column("users", sa.Column("target_carb", sa.Numeric(10, 2), nullable=True))
    op.add_column("users", sa.Column("target_fat", sa.Numeric(10, 2), nullable=True))
    op.add_column("users", sa.Column("target_bmi", sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "target_bmi")
    op.drop_column("users", "target_fat")
    op.drop_column("users", "target_carb")
    op.drop_column("users", "target_protein")
    op.drop_column("users", "target_calories")
    op.drop_column("users", "start_date")
    op.drop_column("users", "status")
    op.drop_column("users", "vegan_status")
    op.drop_column("users", "activity_level")
    op.drop_column("users", "height_cm")
    op.drop_column("users", "weight_kg")
    op.drop_column("users", "gender")
    op.drop_column("users", "age")
