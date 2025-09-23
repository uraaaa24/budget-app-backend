"""insert_default_expense_categories

Revision ID: 90660cead630
Revises: a605d5a26a5b
Create Date: 2025-09-23 05:54:31.836699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90660cead630'
down_revision: Union[str, Sequence[str], None] = 'a605d5a26a5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # デフォルト支出カテゴリの挿入
    op.execute("""
        INSERT INTO categories (id, user_id, name, description, type, is_archived, created_at, updated_at)
        VALUES
            (gen_random_uuid(), NULL, 'Housing', 'Rent, mortgage, property taxes, home maintenance', 'expense', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Food', 'Groceries, dining out, beverages', 'expense', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Clothing', 'Clothes, shoes, accessories', 'expense', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Utilities', 'Electricity, gas, water, sewage', 'expense', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Medical', 'Healthcare, medications, personal care', 'expense', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Communication', 'Phone, internet, cable TV', 'expense', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Childcare', 'Kids expenses, school, toys', 'expense', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Vehicle', 'Car payments, gas, maintenance', 'expense', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Entertainment', 'Movies, hobbies, social activities', 'expense', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Transport', 'Public transport, taxi, parking', 'expense', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Insurance', 'Life, health, property insurance', 'expense', false, NOW(), NOW()),
            (gen_random_uuid(), NULL, 'Other', 'Miscellaneous expenses', 'expense', false, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # デフォルトカテゴリの削除
    op.execute("""
        DELETE FROM categories
        WHERE user_id IS NULL
        AND name IN (
            'Housing', 'Food', 'Clothing', 'Utilities', 'Medical',
            'Communication', 'Childcare', 'Vehicle', 'Entertainment',
            'Transport', 'Insurance', 'Other'
        );
    """)
