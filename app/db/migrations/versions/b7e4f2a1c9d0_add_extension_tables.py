"""Add extension settings and migration tracking tables.

Revision ID: b7e4f2a1c9d0
Revises: a3b4c5d6e7f8
Create Date: 2026-07-05 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b7e4f2a1c9d0"
down_revision = "a3b4c5d6e7f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "extension_settings",
        sa.Column("extension_id", sa.String(length=128), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("extension_id", name=op.f("pk_extension_settings")),
    )
    op.create_table(
        "extension_migrations",
        sa.Column("extension_id", sa.String(length=128), nullable=False),
        sa.Column("revision", sa.String(length=64), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("extension_id", "revision", name=op.f("pk_extension_migrations")),
    )


def downgrade() -> None:
    op.drop_table("extension_migrations")
    op.drop_table("extension_settings")
