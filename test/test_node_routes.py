from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4
from src.core_api.db.worker_node_db import InvalidUpdate
from src.core_api.app import app
from src.core_api.models.worker_node import WorkerNode, WorkerNodeUpdates
from fastapi.testclient import TestClient
import pytest

@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_node_service():

    with patch("src.core_api.routes.node_routes.NodeService", new=MagicMock()) as mock, \
         patch("src.core_api.routes.node_routes.NodeDatabase", new=MagicMock()):
        yield mock


def test_update_success(test_client: TestClient, mock_node_service: MagicMock):
    node = WorkerNode(node_id=uuid4(), job_slots=1, cpu_count=1, memory_allocated=10)
    mock_node_service.return_value.update_node.return_value = node

    node_updates = WorkerNodeUpdates(job_slots=1, cpu_count=1, memory_allocated=10)
    node_dict = node_updates.model_dump()

    response = test_client.post(
        f"/worker-node/update?node_id={node.node_id}",
        json=node_dict
    )

    assert response.status_code == 200
    expected_node = node.model_dump()
    expected_node["node_id"] = str(node.node_id)
    assert response.json() == expected_node

def test_update_job_slots_less_than_zero(test_client: TestClient, mock_node_service: MagicMock):
    node: dict[Any, Any] = {"node_id":uuid4(), "job_slots":-1, "cpu_count":-1, "memory_allocated":-1}
    # mock_node_service.return_value.update_node.side_effect = InvalidUpdate

    node_updates: dict[Any, Any] = {"job_slots":-1, "cpu_count":-1, "memory_allocated":-1}

    response = test_client.post(
        f"/worker-node/update?node_id={node["node_id"]}",
        json=node_updates
    )

    assert response.status_code == 422

def test_no_updates(test_client: TestClient, mock_node_service: MagicMock):
    node: dict[Any, Any] = {"node_id":uuid4(), "job_slots":-1, "cpu_count":-1, "memory_allocated":-1}
    mock_node_service.return_value.update_node.side_effect = InvalidUpdate

    node_updates = WorkerNodeUpdates(job_slots=1, cpu_count=1, memory_allocated=10)
    node_dict = node_updates.model_dump()

    response = test_client.post(
        f"/worker-node/update?node_id={node["node_id"]}",
        json=node_dict
    )

    assert response.status_code == 409



