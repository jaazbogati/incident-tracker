

def test_login_missing_fields(client):
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 400