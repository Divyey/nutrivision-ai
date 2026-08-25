"""Allow typed catalog meals: nullable class_id, food_id, unit.

Revision ID: 0006_typed_meal_entries
Revises: 0005_foods_catalog
Create Date: 2026-08-24
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_typed_meal_entries"
down_revision = "0005_foods_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "meal_entries",
        "class_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "meal_entries",
        "label",
        existing_type=sa.String(length=64),
        type_=sa.String(length=128),
        existing_nullable=False,
    )
    op.add_column("meal_entries", sa.Column("food_id", sa.Uuid(), nullable=True))
    op.add_column(
        "meal_entries", sa.Column("unit", sa.String(length=16), nullable=True)
    )
    op.create_foreign_key(
        "fk_meal_entries_food_id",
        "meal_entries",
        "foods",
        ["food_id"],
        ["id"],
    )
    op.create_check_constraint(
        "ck_meal_entries_class_or_food",
        "meal_entries",
        "class_id IS NOT NULL OR food_id IS NOT NULL",
    )


def downgrade() -> None:
    op.drop_constraint("ck_meal_entries_class_or_food", "meal_entries", type_="check")
    op.drop_constraint("fk_meal_entries_food_id", "meal_entries", type_="foreignkey")
    op.drop_column("meal_entries", "unit")
    op.drop_column("meal_entries", "food_id")
    op.alter_column(
        "meal_entries",
        "label",
        existing_type=sa.String(length=128),
        type_=sa.String(length=64),
        existing_nullable=False,
    )
    op.alter_column(
        "meal_entries",
        "class_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
