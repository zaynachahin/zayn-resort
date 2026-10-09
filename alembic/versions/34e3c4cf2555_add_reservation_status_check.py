"""add reservation status check

Revision ID: 34e3c4cf2555
Revises: b9d262776948
Create Date: 2026-10-09 19:04:16.331046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34e3c4cf2555'
down_revision: Union[str, Sequence[str], None] = 'b9d262776948'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "reservation_status_check",
        "reservations",
        "status IN ('confirmed', 'checked_in', 'checked_out', 'cancelled')",
    )


def downgrade() -> None:
    op.drop_constraint("reservation_status_check", "reservations", type_="check")