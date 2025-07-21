from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_root(client: TestClient) -> None:
    """API rootエンドポイントのテスト"""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json() == {"message": "Budget App API v1"}