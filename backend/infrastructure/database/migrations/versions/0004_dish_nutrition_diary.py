"""Add dish_nutrition, meal_entries, and water_entries.

Revision ID: 0004_dish_nutrition_diary
Revises: 0003_add_user_allergy
Create Date: 2026-08-23

dish_nutrition is created empty. Do not seed plausible per-100g values here.
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_dish_nutrition_diary"
down_revision = "0003_add_user_allergy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dish_nutrition",
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("calories_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("protein_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("carb_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("fat_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("default_serving_grams", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("class_id"),
    )
    op.create_table(
        "meal_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("logged_on", sa.Date(), nullable=False),
        sa.Column("slot", sa.String(length=16), nullable=False),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=64), nullable=False),
        sa.Column("quantity", sa.Numeric(8, 2), nullable=False),
        sa.Column("calories", sa.Numeric(10, 2), nullable=False),
        sa.Column("protein", sa.Numeric(10, 2), nullable=False),
        sa.Column("carb", sa.Numeric(10, 2), nullable=False),
        sa.Column("fat", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_meal_entries_user_logged_on",
        "meal_entries",
        ["user_id", "logged_on"],
    )
    op.create_index(
        "ix_meal_entries_user_logged_on_slot",
        "meal_entries",
        ["user_id", "logged_on", "slot"],
    )
    op.create_table(
        "water_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("logged_on", sa.Date(), nullable=False),
        sa.Column("milliliters", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_water_entries_user_logged_on",
        "water_entries",
        ["user_id", "logged_on"],
    )


def downgrade() -> None:
    op.drop_index("ix_water_entries_user_logged_on", table_name="water_entries")
    op.drop_table("water_entries")
    op.drop_index("ix_meal_entries_user_logged_on_slot", table_name="meal_entries")
    op.drop_index("ix_meal_entries_user_logged_on", table_name="meal_entries")
    op.drop_table("meal_entries")
    op.drop_table("dish_nutrition")
