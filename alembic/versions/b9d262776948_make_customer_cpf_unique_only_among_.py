"""make customer cpf unique only among active

Revision ID: b9d262776948
Revises: 8d7a6b40e408
Create Date: 2026-10-09 17:30:15.358628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9d262776948'
down_revision: Union[str, Sequence[str], None] = '8d7a6b40e408'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("customers_cpf_key", "customers", type_="unique")
    op.create_index(
        "customers_cpf_active_unique",
        "customers",
        ["cpf"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("customers_cpf_active_unique", table_name="customers")
    op.create_unique_constraint("customers_cpf_key", "customers", ["cpf"])