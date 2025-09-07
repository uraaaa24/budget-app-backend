"""Temporarily disable foreign key constraints for transactions

Revision ID: 004
Revises: 003
Create Date: 2025-09-07 01:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: str | Sequence[str] | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop foreign key constraints temporarily
    op.drop_constraint(
        op.f("fk_transactions_account_id_accounts"), "transactions", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_transactions_category_id_categories"), "transactions", type_="foreignkey"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add foreign key constraints
    op.create_foreign_key(
        op.f("fk_transactions_category_id_categories"),
        "transactions",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_transactions_account_id_accounts"),
        "transactions",
        "accounts",
        ["account_id"],
        ["id"],
        ondelete="CASCADE",
    )
