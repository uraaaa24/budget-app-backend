"""insert_default_income_categories

Revision ID: d9736421a334
Revises: 90660cead630
Create Date: 2025-09-23 06:42:39.809040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9736421a334'
down_revision: Union[str, Sequence[str], None] = '90660cead630'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # デフォルト収入カテゴリの挿入
    op.execute("""
        INSERT INTO categories (id, user_id, name, description, type, is_archived, created_at, updated_at)
        VALUES
            (gen_random_uuid(), NULL, 'Salary', 'Regular salary from employment', 'income', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Business', 'Side business and freelance income', 'income', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Investment', 'Returns from stocks, bonds, dividends', 'income', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Estate', 'Real estate rental income', 'income', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Pension', 'Retirement pension and social security', 'income', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Subsidy', 'Government subsidies and benefits', 'income', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Gift', 'Gifts and financial support from family', 'income', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Other', 'Other sources of income', 'income', false, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # デフォルト収入カテゴリの削除
    op.execute("""
        DELETE FROM categories
        WHERE user_id IS NULL
        AND name IN (
            'Salary', 'Business', 'Investment', 'Estate',
            'Pension', 'Subsidy', 'Gift', 'Other'
        )
        AND type = 'income';
    """)
