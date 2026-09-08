"""create_room_categories_table

Revision ID: 84637c26822a
Revises: 53e6d6cad57b
Create Date: 2026-09-04 19:58:43.658775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84637c26822a'
down_revision: Union[str, Sequence[str], None] = '53e6d6cad57b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "room_categories",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("daily_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("deleted_at", sa.DateTime()),
    )

    op.create_index(
        "room_categories_name_active_unique",
        "room_categories",
        ["name"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("room_categories_name_active_unique", table_name="room_categories")
    op.drop_table("room_categories")