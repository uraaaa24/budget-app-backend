"""Make account_id nullable temporarily

Revision ID: 005
Revises: 004
Create Date: 2025-09-07 01:50:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: str | Sequence[str] | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make account_id nullable
    op.alter_column('transactions', 'account_id',
                    existing_type=postgresql.UUID(as_uuid=True),
                    nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Make account_id not nullable again
    op.alter_column('transactions', 'account_id',
                    existing_type=postgresql.UUID(as_uuid=True),
                    nullable=False)
