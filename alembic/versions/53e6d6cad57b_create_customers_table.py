"""create_customers_table

Revision ID: 53e6d6cad57b
Revises: 
Create Date: 2026-09-04 19:31:17.034092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53e6d6cad57b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.UUID(), primary_key = True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("full_name", sa.String(255), nullable = False),
        sa.Column("date_of_birth", sa.Date(), nullable = False),
        sa.Column("cpf", sa.String(11), nullable = False, unique = True),
        sa.Column("newsletter_opt_in", sa.Boolean(), nullable = False),
        sa.Column("created_at", sa.DateTime(), nullable = False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime()),
        sa.Column("deleted_at", sa.DateTime())
    )


def downgrade() -> None:
    op.drop_table("customers")