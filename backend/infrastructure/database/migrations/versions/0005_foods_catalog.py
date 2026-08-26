"""Add foods, food_aliases, and food_servings.

Revision ID: 0005_foods_catalog
Revises: 0004_dish_nutrition_diary
Create Date: 2026-08-24

Tables are created empty. Seed from data/foods_catalog.csv via
scripts/upsert_foods_catalog.py. Do not bulk-insert INDB here.
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_foods_catalog"
down_revision = "0004_dish_nutrition_diary"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "foods",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("detect_class_id", sa.Integer(), nullable=True),
        sa.Column("calories_per_100g", sa.Numeric(10, 2), nullable=True),
        sa.Column("protein_per_100g", sa.Numeric(10, 2), nullable=True),
        sa.Column("carb_per_100g", sa.Numeric(10, 2), nullable=True),
        sa.Column("fat_per_100g", sa.Numeric(10, 2), nullable=True),
        sa.Column("density_g_per_ml", sa.Numeric(10, 4), nullable=True),
        sa.Column("source_dataset", sa.String(length=32), nullable=True),
        sa.Column("source_id", sa.String(length=32), nullable=True),
        sa.Column("source_note", sa.String(length=256), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("detect_class_id"),
    )
    op.create_table(
        "food_aliases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("food_id", sa.Uuid(), nullable=False),
        sa.Column("alias", sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(["food_id"], ["foods.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alias", name="uq_food_aliases_alias"),
    )
    op.create_index("ix_food_aliases_food_id", "food_aliases", ["food_id"])
    op.create_table(
        "food_servings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("food_id", sa.Uuid(), nullable=False),
        sa.Column("unit", sa.String(length=16), nullable=False),
        sa.Column("grams", sa.Numeric(10, 2), nullable=False),
        sa.Column("milliliters", sa.Numeric(10, 2), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["food_id"], ["foods.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("food_id", "unit", name="uq_food_servings_food_unit"),
    )


def downgrade() -> None:
    op.drop_table("food_servings")
    op.drop_index("ix_food_aliases_food_id", table_name="food_aliases")
    op.drop_table("food_aliases")
    op.drop_table("foods")
