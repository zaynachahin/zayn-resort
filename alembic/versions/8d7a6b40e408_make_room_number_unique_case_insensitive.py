"""make_room_number_unique_case_insensitive

Revision ID: 8d7a6b40e408
Revises: b120b0987a7d
Create Date: 2026-10-02 23:06:50.113086

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d7a6b40e408'
down_revision: Union[str, Sequence[str], None] = 'b120b0987a7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "rooms_number_unique", 
        "rooms", 
        type_="unique",
    )

    op.create_index(
        "rooms_number_lower_active_unique",
        "rooms",
        [sa.text("LOWER(number)")],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("rooms_number_lower_active_unique", table_name="rooms")
    
    op.create_unique_constraint("rooms_number_unique", "rooms", ["number"])