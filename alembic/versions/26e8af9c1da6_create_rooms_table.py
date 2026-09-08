"""create_rooms_table

Revision ID: 26e8af9c1da6
Revises: 84637c26822a
Create Date: 2026-09-04 19:58:44.674371

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26e8af9c1da6'
down_revision: Union[str, Sequence[str], None] = '84637c26822a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rooms",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("room_category_id", sa.UUID(), sa.ForeignKey("room_categories.id"), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("number", sa.String(10), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("deleted_at", sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table("rooms")