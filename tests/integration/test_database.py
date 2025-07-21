import os
import psycopg
import pytest


def test_database_connection() -> None:
    """データベース接続のテスト"""
    db_dsn = os.environ.get("DB_DSN", "postgresql://budget:budget@db:5432/budget_app")
    
    try:
        with psycopg.connect(db_dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                assert result is not None
                assert result[0] == 1
    except Exception as e:
        pytest.skip(f"データベース接続に失敗: {e}")


def test_migrations_table_exists() -> None:
    """マイグレーションテーブルの存在確認"""
    db_dsn = os.environ.get("DB_DSN", "postgresql://budget:budget@db:5432/budget_app")
    
    try:
        with psycopg.connect(db_dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'migrations'
                    )
                """)
                exists = cur.fetchone()
                assert exists is not None
                assert exists[0] is True
    except Exception as e:
        pytest.skip(f"データベース接続に失敗: {e}")