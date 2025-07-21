import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """イベントループをセッションスコープで作成"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """FastAPIテストクライアント"""
    return TestClient(app)


@pytest.fixture
def test_db_dsn() -> str:
    """テスト用データベースDSN"""
    return os.environ.get(
        "TEST_DB_DSN", 
        "postgresql://budget:budget@localhost:5432/budget_app_test"
    )