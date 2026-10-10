"""make room description nullable

Revision ID: f52f5a52ee03
Revises: 683cbeba0d53
Create Date: 2026-10-09 21:28:54.961903

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f52f5a52ee03'
down_revision: Union[str, Sequence[str], None] = '683cbeba0d53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "rooms",
        "description",
        existing_type=sa.String(length=500),
        nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        "rooms",
        "description",
        existing_type=sa.String(length=500),
        nullable=False
    )