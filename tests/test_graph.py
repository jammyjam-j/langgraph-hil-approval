import asyncio
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.graph import get_graph_executor
from app.schemas import RequestInput, ApprovalResponse


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.asyncio
async def test_initial_state(client: TestClient):
    payload = {"requester": "alice", "document_id": 42}
    response = client.post("/submit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["current_node"] == "awaiting_approval"


@pytest.mark.asyncio
async def test_successful_approval_path(client: TestClient):
    payload = {"requester": "bob", "document_id": 84}
    submit_resp = client.post("/submit", json=payload)
    assert submit_resp.status_code == 200
    state = submit_resp.json()

    exec = get_graph_executor()
    node_result = await exec.step(state["workflow_state"], {"action": "approve"})
    next_state = node_result.state

    post_resp = client.post(f"/continue/{state['request_id']}", json={"action": "approve"})
    assert post_resp.status_code == 200
    final_data = post_resp.json()
    assert final_data["status"] == "approved"
    assert isinstance(final_data["timestamp"], str)
    assert datetime.fromisoformat(final_data["timestamp"]) <= datetime.utcnow()


@pytest.mark.asyncio
async def test_rejection_path(client: TestClient):
    payload = {"requester": "charlie", "document_id": 128}
    submit_resp = client.post("/submit", json=payload)
    assert submit_resp.status_code == 200
    state = submit_resp.json()

    exec = get_graph_executor()
    node_result = await exec.step(state["workflow_state"], {"action": "reject"})
    next_state = node_result.state

    post_resp = client.post(f"/continue/{state['request_id']}", json={"action": "reject"})
    assert post_resp.status_code == 200
    final_data = post_resp.json()
    assert final_data["status"] == "rejected"
    assert isinstance(final_data["timestamp"], str)
    assert datetime.fromisoformat(final_data["timestamp"]) <= datetime.utcnow()


@pytest.mark.asyncio
async def test_invalid_action(client: TestClient):
    payload = {"requester": "dave", "document_id": 256}
    submit_resp = client.post("/submit", json=payload)
    assert submit_resp.status_code == 200
    state = submit_resp.json()

    exec = get_graph_executor()
    with pytest.raises(ValueError):
        await exec.step(state["workflow_state"], {"action": "unknown"})

    post_resp = client.post(f"/continue/{state['request_id']}", json={"action": "unknown"})
    assert post_resp.status_code == 400
    error_data = post_resp.json()
    assert "detail" in error_data

@pytest.mark.asyncio
async def test_concurrent_submissions(client: TestClient):
    async def submit(doc_id: int) -> dict:
        payload = {"requester": f"user{doc_id}", "document_id": doc_id}
        resp = client.post("/submit", json=payload)
        assert resp.status_code == 200
        return resp.json()

    tasks = [asyncio.create_task(submit(i)) for i in range(5, 10)]
    results = await asyncio.gather(*tasks)

    ids = {res["request_id"] for res in results}
    assert len(ids) == 5

    for res in results:
        exec = get_graph_executor()
        node_result = await exec.step(res["workflow_state"], {"action": "approve"})
        assert node_result.state["status"] == "approved"