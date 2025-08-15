import pytest
from unittest.mock import MagicMock
from src.core_api.models.node import Node
from src.core_api.services.node_service import NodeService

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def service(mock_db):
    return NodeService(mock_db)

def test_set_job_slots_valid(service, mock_db):
    """Should update job slots when given valid input"""
    expected_node = Node(node_id="node1", job_slots=3)
    mock_db.update_node.return_value = expected_node

    result = service.set_job_slots("node1", 3)

    assert result == expected_node
    mock_db.update_node.assert_called_once_with("node1", {"job_slots": 3})

def test_set_job_slots_negative(service, mock_db):
    """Should raise ValueError if slots are negative"""
    with pytest.raises(ValueError, match="cannot be empty"):
        service.set_job_slots("node1", -1)
    mock_db.update_node.assert_not_called()

def test_set_job_slots_invalid_type(service, mock_db):
    """Should raise ValueError if slots are not an int"""
    with pytest.raises(ValueError, match="Invalid job slots value"):
        service.set_job_slots("node1", "not-a-number")  # type: ignore
    mock_db.update_node.assert_not_called()
