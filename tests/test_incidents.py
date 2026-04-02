def test_create_incident_requires_auth(client):
    response = client.post("/api/v1/incidents", json={
        "title": "Test Incident",
        "description": "This is a test incident",
        "severity": "High"
    })
    assert response.status_code == 401