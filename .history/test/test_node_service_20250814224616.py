import pytest
from unittest.mock import MagicMock
from src.core_api.services.node_service import NodeService
from src.core_api.models.node import Node

@pytest.fixture
def mock_db():
    mock = MagicMock()
    mock.update_node.return_value = None  # Default return
    return mock

def test_set_job_slots_success(mock_db):
    # Setup mock
    test_node = Node(node_id="n1", job_slots=5)
    mock_db.update_node.return_value = test_node
    
    # Test
    service = NodeService(mock_db)
    result = service.set_job_slots("n1", 5)
    
    # Verify
    assert result == test_node
    mock_db.update_node.assert_called_once_with("n1", {"job_slots": 5})

def test_set_job_slots_not_found(mock_db):
    service = NodeService(mock_db)
    assert service.set_job_slots("missing", 5) is None

def test_set_job_slots_invalid(mock_db):
    service = NodeService(mock_db)
    with pytest.raises(ValueError):
        service.set_job_slots("n1", -1)  # Negative slots

def test_set_job_slots_empty_node(mock_db):
    service = NodeService(mock_db)
    with pytest.raises(ValueError):
        service.set_job_slots("", 5)  # Empty node_id