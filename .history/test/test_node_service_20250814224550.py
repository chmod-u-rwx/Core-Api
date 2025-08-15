import pytest
from unittest.mock import MagicMock
from src.services.node_service import NodeService
from src.models.node import Node


@pytest.fixture
def mock_node_db():
    return MagicMock()


@pytest.fixture
def node_service(mock_node_db):
    return NodeService(mock_node_db)


def test_set_available_job_slots_success(node_service, mock_node_db):
    node_id = "node123"
    updated_node = Node(node_id=node_id, job_slots=5)
    mock_node_db.update_node.return_value = updated_node

    result = node_service.set_available_job_slots(node_id, 5)

    mock_node_db.update_node.assert_called_once_with(node_id, {"job_slots": 5})
    assert result == updated_node


def test_set_available_job_slots_negative_value_raises(node_service):
    with pytest.raises(ValueError, match="Job slots cannot be negative."):
        node_service.set_available_job_slots("node123", -1)


def test_set_available_job_slots_node_not_found(node_service, mock_node_db):
    mock_node_db.update_node.return_value = None

    result = node_service.set_available_job_slots("node123", 3)

    assert result is None
    mock_node_db.update_node.assert_called_once_with("node123", {"job_slots": 3})
