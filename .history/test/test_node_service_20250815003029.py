import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError
from src.core_api.db.node_database import NodeDatabase
from src.core_api.models.node import Node
from src.core_api.services.node_service import NodeService

@pytest.fixture
def mock_db():
    """Fixture providing a properly configured mock NodeDatabase"""
    mock = MagicMock()
    mock.update_node.return_value = None  # Default return value
    return mock

@pytest.fixture
def node_service(mock_db):
    """Fixture providing a NodeService with mocked database"""
    return NodeService(mock_db)

# ---- Success Cases ----
def test_set_job_slots_success(node_service, mock_db):
    """Test successful job slot update"""
    # Setup
    test_node = Node(node_id="node1", job_slots=5)
    mock_db.update_node.return_value = test_node
    
    # Execute
    result = node_service.set_job_slots("node1", 5)
    
    # Verify
    assert result == test_node
    mock_db.update_node.assert_called_once_with("node1", {"job_slots": 5})

# ---- Validation Error Cases ----
def test_negative_job_slots(node_service, mock_db):
    """Test negative slots raise ValueError"""
    with pytest.raises(ValueError, match="cannot be negative"):
        node_service.set_job_slots("node1", -1)
    mock_db.update_node.assert_not_called()

def test_non_integer_slots(node_service, mock_db):
    """Test non-integer slots raise ValueError"""
    with pytest.raises(ValueError, match="must be an integer"):
        node_service.set_job_slots("node1", "five")  # type: ignore
    mock_db.update_node.assert_not_called()

# ---- Database Interaction Cases ----
def test_nonexistent_node(node_service, mock_db):
    """Test non-existent node returns None"""
    mock_db.update_node.return_value = None
    assert node_service.set_job_slots("ghost", 5) is None
    mock_db.update_node.assert_called_once_with("ghost", {"job_slots": 5})