"""add reservation room id index

Revision ID: 683cbeba0d53
Revises: 34e3c4cf2555
Create Date: 2026-10-09 21:14:13.580204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '683cbeba0d53'
down_revision: Union[str, Sequence[str], None] = '34e3c4cf2555'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "reservations_room_id_active_idx",
        "reservations",
        ["room_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("reservations_room_id_active_idx", table_name="reservations")