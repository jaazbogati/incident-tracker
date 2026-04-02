import uuid

def test_full_incident_workflow(client):
    
    email = f"user_{uuid.uuid4()}@test.com"

    # 1. Register a new user
    register_response = client.post("/api/v1/auth/register", json={
        "username": "bank Job",
        "email": email,
        "password": "testpassword"
    })

    assert register_response.status_code == 201

    # 2. Login with the new user
    login_response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "testpassword"
    })

    assert login_response.status_code == 200

    token = login_response.get_json()["data"]["token"]


    headers = {"Authorization": f"Bearer {token}"}

    #3. Create a new incident
    create_response = client.post("/api/v1/incidents", json={
        "title": "Test Incident",
        "description": "This is a test incident",
        "severity": "High"
    }, headers=headers)

    assert create_response.status_code == 201

    incident_data = create_response.get_json()["data"]
    incident_id = incident_data["id"]

    # 4. Update the incident status
    update_response = client.patch(f"/api/v1/incidents/{incident_id}", json={
        "status": "In Progress"
    }, headers=headers)

    assert update_response.status_code == 200

    updated = update_response.get_json()["data"]
    assert "status" in updated["updated_fields"]

    # 5.Close the incident
    close_response = client.patch(f"/api/v1/incidents/{incident_id}", json={
        "status": "Closed"
    }, headers=headers)

    assert close_response.status_code == 200 

    # 6. Get the incident details to verify status
    get_response = client.get(f"/api/v1/incidents/{incident_id}", headers=headers
    )

    assert get_response.status_code == 200
    assert get_response.get_json()["data"]["status"] == "Closed"