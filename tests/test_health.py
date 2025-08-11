"""ヘルスチェックAPIのテスト"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """ヘルスチェックが正常に動作することを確認"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_database_health_check(client: TestClient) -> None:
    """データベース接続のヘルスチェックを確認"""
    response = client.get("/health/db")
    assert response.status_code == 200

    data = response.json()
    assert "database" in data
    assert data["database"]["status"] in ["ok", "error"]
