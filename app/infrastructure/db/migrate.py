import os
import psycopg


def main() -> None:
    """データベースのマイグレーションを実行"""
    db_dsn = os.environ.get("DB_DSN", "postgresql://budget:budget@db:5432/budget_app")
    
    try:
        with psycopg.connect(db_dsn) as conn:
            with conn.cursor() as cur:
                print("データベース接続成功")
                # 基本的なテーブル作成
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS migrations (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # マイグレーション記録を確認
                cur.execute("SELECT name FROM migrations WHERE name = %s", ("initial_setup",))
                if not cur.fetchone():
                    print("初期セットアップを実行中...")
                    
                    # ユーザーテーブル
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            name VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # 予算カテゴリテーブル
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS budget_categories (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            name VARCHAR(255) NOT NULL,
                            budget_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # 支出記録テーブル
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS expenses (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            category_id INTEGER REFERENCES budget_categories(id) ON DELETE SET NULL,
                            amount DECIMAL(10, 2) NOT NULL,
                            description TEXT,
                            expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # マイグレーション記録を追加
                    cur.execute(
                        "INSERT INTO migrations (name) VALUES (%s)",
                        ("initial_setup",)
                    )
                    
                    print("初期セットアップ完了")
                else:
                    print("データベースは既にセットアップ済みです")
                
                conn.commit()
                print("マイグレーション完了")
                
    except Exception as e:
        print(f"マイグレーションエラー: {e}")
        raise


if __name__ == "__main__":
    main()