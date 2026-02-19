import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Soccer Team" in data
    assert "Basketball Club" in data


def test_signup_and_unregister():
    email = "pytestuser@mergington.edu"
    activity = "Soccer Team"
    # Signup
    signup_resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert signup_resp.status_code == 200
    assert f"Signed up {email}" in signup_resp.json()["message"]
    # Check participant added
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]
    # Unregister
    unregister_resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert unregister_resp.status_code == 200
    assert f"Removed {email}" in unregister_resp.json()["message"]
    # Check participant removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]


def test_signup_duplicate():
    email = "pytestuser2@mergington.edu"
    activity = "Basketball Club"
    # Signup first time
    client.post(f"/activities/{activity}/signup", params={"email": email})
    # Signup again (should fail)
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"]
    # Cleanup
    client.post(f"/activities/{activity}/unregister", params={"email": email})


def test_unregister_nonexistent():
    email = "nonexistent@mergington.edu"
    activity = "Drama Club"
    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 404
    assert "Participant not found" in resp.json()["detail"]
