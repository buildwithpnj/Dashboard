import pytest
from fastapi.testclient import TestClient

def test_family_checkin_normal_flow(client):
    """Asserts that regular check-in updates return a normal status without triggers."""
    payload = {
        "user_id": "default_user",
        "message_text": "Sab theek hai beta, main thik hu.",
        "session_id": "test-session-fam-1"
    }
    response = client.post("/v1/coach/family/checkin", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["checkin_status"] == "normal"
    assert data["escalation_triggered"] is False
    assert len(data["escalation_contacts"]) > 0

def test_family_checkin_escalation_flow(client):
    """Asserts that pain or injury statements trigger escalations and return contacts list."""
    payload = {
        "user_id": "default_user",
        "message_text": "Mera pair fisal gaya aur chhati me dard hai.",
        "session_id": "test-session-fam-2"
    }
    response = client.post("/v1/coach/family/checkin", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["checkin_status"] == "escalated"
    assert data["escalation_triggered"] is True
    assert len(data["escalation_contacts"]) > 0
    
    # Assert contacts list correctly references Prakash
    assert data["escalation_contacts"][0]["name"] == "Prakash"
    assert data["escalation_contacts"][0]["relationship"] == "Son"
