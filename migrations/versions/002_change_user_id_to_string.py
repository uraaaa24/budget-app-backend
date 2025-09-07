"""Change user_id from UUID to String

Revision ID: 002
Revises: 001
Create Date: 2025-09-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, Sequence[str], None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Change user_id column from UUID to String
    op.alter_column('transactions', 'user_id',
                    existing_type=postgresql.UUID(as_uuid=True),
                    type_=sa.String(length=255),
                    existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Change user_id column from String back to UUID
    op.alter_column('transactions', 'user_id',
                    existing_type=sa.String(length=255),
                    type_=postgresql.UUID(as_uuid=True),
                    existing_nullable=False)
