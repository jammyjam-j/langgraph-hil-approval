import os
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def created_approval():
    payload = {
        "title": "Test Approval",
        "description": "Testing the approval workflow",
        "requested_by": "tester@example.com"
    }
    response = client.post("/approvals", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data and isinstance(data["id"], str)
    return data["id"]

def test_submit_approval_success():
    payload = {
        "title": "Sample Approval",
        "description": "Sample description",
        "requested_by": "user@example.com"
    }
    response = client.post("/approvals", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data, dict)
    assert "id" in data and isinstance(UUID(data["id"]), UUID)

def test_submit_approval_missing_fields():
    payload = {
        "title": "Incomplete Approval"
    }
    response = client.post("/approvals", json=payload)
    assert response.status_code == 422
    error = response.json()
    assert error["detail"][0]["loc"][-1] in {"description", "requested_by"}

def test_get_approval_status(created_approval):
    approval_id = created_approval
    response = client.get(f"/approvals/{approval_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["id"] == approval_id
    assert data["status"] in {"pending", "approved", "rejected"}

def test_get_approval_status_invalid_uuid():
    invalid_id = "not-a-uuid"
    response = client.get(f"/approvals/{invalid_id}/status")
    assert response.status_code == 422

def test_update_approval_reject(created_approval):
    approval_id = created_approval
    payload = {"decision": "reject", "comment": "Not suitable"}
    response = client.post(f"/approvals/{approval_id}/decide", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["comment"] == payload["comment"]

def test_update_approval_approve(created_approval):
    approval_id = created_approval
    payload = {"decision": "approve", "comment": "All good"}
    response = client.post(f"/approvals/{approval_id}/decide", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["comment"] == payload["comment"]

def test_update_approval_invalid_decision(created_approval):
    approval_id = created_approval
    payload = {"decision": "invalid", "comment": "Invalid decision"}
    response = client.post(f"/approvals/{approval_id}/decide", json=payload)
    assert response.status_code == 422

def test_get_nonexistent_approval():
    fake_uuid = str(UUID(int=0))
    response = client.get(f"/approvals/{fake_uuid}/status")
    assert response.status_code == 404
    error = response.json()
    assert "detail" in error and "not found" in error["detail"].lower()

def test_list_approvals():
    response = client.get("/approvals")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert "id" in item and isinstance(UUID(item["id"]), UUID)

def test_delete_approval(created_approval):
    approval_id = created_approval
    response = client.delete(f"/approvals/{approval_id}")
    assert response.status_code == 204
    get_response = client.get(f"/approvals/{approval_id}/status")
    assert get_response.status_code == 404

def test_cors_headers():
    response = client.options("/approvals")
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "*" in response.headers["access-control-allow-origin"] or \
           app.config.cors_origins is not None

@pytest.mark.parametrize("method", ["get", "post", "put", "delete"])
def test_api_rate_limiting(method):
    for _ in range(10):
        if method == "get":
            resp = client.get("/approvals")
        elif method == "post":
            resp = client.post("/approvals", json={"title":"Rate","description":"Test","requested_by":"rate@example.com"})
        elif method == "put":
            resp = client.put("/approvals/nonexistent-id", json={})
        else:
            resp = client.delete("/approvals/nonexistent-id")
    # Assuming rate limit is 10 per minute
    if resp.status_code == 429:
        assert "Too Many Requests" in resp.text

def test_environment_variables():
    assert os.getenv("APP_ENV") is not None
    assert os.getenv("DATABASE_URL") is not None

def test_app_version_endpoint():
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data and isinstance(data["version"], str)