"""create_reservations_table

Revision ID: 29de4088bbdf
Revises: 26e8af9c1da6
Create Date: 2026-09-04 19:58:45.508482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29de4088bbdf'
down_revision: Union[str, Sequence[str], None] = '26e8af9c1da6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reservations",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("customer_id", sa.UUID(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("room_id", sa.UUID(), sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("check_in", sa.Date(), nullable=False),
        sa.Column("check_out", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'confirmed'")),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("deleted_at", sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table("reservations")