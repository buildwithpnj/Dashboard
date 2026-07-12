def test_health_check(client):
    """Verifies that the /v1/coach/health endpoint yields the expected operational metadata."""
    response = client.get("/v1/coach/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "app_name" in data
    assert "app_env" in data
