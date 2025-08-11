"""テスト用の共通設定とフィクスチャ"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# テスト用インメモリデータベース
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def test_db():
    """テスト用データベースセッション"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """各テストで使用するデータベースセッション"""
    session = test_db()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """テスト用FastAPIクライアント"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_id():
    """テスト用ユーザーID"""
    from uuid import uuid4

    return uuid4()


@pytest.fixture
def sample_account_id():
    """テスト用アカウントID"""
    from uuid import uuid4

    return uuid4()


@pytest.fixture
def sample_transaction_data(sample_user_id, sample_account_id):
    """テスト用トランザクションデータ"""
    from datetime import date

    return {
        "user_id": str(sample_user_id),
        "account_id": str(sample_account_id),
        "type": "expense",
        "amount": 10000,
        "occurred_at": date.today().isoformat(),
        "description": "テスト用支出",
    }
