"""make_room_category_name_unique_case_insensitive

Revision ID: b120b0987a7d
Revises: 29de4088bbdf
Create Date: 2026-10-02 17:44:28.697378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b120b0987a7d'
down_revision: Union[str, Sequence[str], None] = '29de4088bbdf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("room_categories_name_active_unique", table_name="room_categories")

    op.create_index(
        "room_categories_name_lower_active_unique",
        "room_categories",
        [sa.text("LOWER(name)")],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("room_categories_name_lower_active_unique", table_name="room_categories")

    op.create_index(
        "room_categories_name_active_unique",
        "room_categories",
        ["name"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )