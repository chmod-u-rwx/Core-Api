import pytest
from unittest.mock import MagicMock, patch
from typing import Optional
from pydantic import ValidationError
from src.core_api.models.node import Node
from src.core_api.services.node_service import NodeService

@pytest.fixture
def mock_db():
    """Fixture providing a mock NodeDatabase instance"""
    mock = MagicMock()
    mock.update_node.return_value = None  # Default return for non-existent nodes
    return mock

@pytest.fixture
def node_service(mock_db):
    """Fixture providing a NodeService instance with mock database"""
    return NodeService(mock_db)

# ---- Success Cases ----
def test_set_job_slots_valid(node_service, mock_db):
    """Test successfully updating job slots for an existing node"""
    # Setup mock return
    expected_node = Node(node_id="node1", job_slots=5)
    mock_db.update_node.return_value = expected_node
    
    # Execute
    result = node_service.set_job_slots("node1", 5)
    
    # Verify
    assert result == expected_node
    mock_db.update_node.assert_called_once_with("node1", {"job_slots": 5})

def test_set_job_slots_zero(node_service, mock_db):
    """Test setting slots to zero is allowed"""
    test_node = Node(node_id="node1", job_slots=0)
    mock_db.update_node.return_value = test_node
    
    result = node_service.set_job_slots("node1", 0)
    assert result.job_slots == 0

# ---- Error Cases ----
def test_set_job_slots_negative(node_service, mock_db):
    """Test negative slot values raise ValueError"""
    with pytest.raises(ValueError, match="cannot be empty"):
        node_service.set_job_slots("node1", -1)
    mock_db.update_node.assert_not_called()

def test_set_job_slots_invalid_node_id(node_service, mock_db):
    """Test invalid node_id format raises ValidationError"""
    with pytest.raises(ValueError, match="Invalid job slots value"):
        node_service.set_job_slots("", 5)  # Empty node_id
    mock_db.update_node.assert_not_called()

def test_set_job_slots_nonexistent_node(node_service, mock_db):
    """Test non-existent node returns None"""
    mock_db.update_node.return_value = None
    assert node_service.set_job_slots("missing", 5) is None
    mock_db.update_node.assert_called_once_with("missing", {"job_slots": 5})

# ---- Edge Cases ----
def test_set_job_slots_max_value(node_service, mock_db):
    """Test large valid slot values"""
    large_number = 2**31 - 1  # Max 32-bit signed int
    test_node = Node(node_id="node1", job_slots=large_number)
    mock_db.update_node.return_value = test_node
    
    result = node_service.set_job_slots("node1", large_number)
    assert result.job_slots == large_number

def test_set_job_slots_string_input(node_service, mock_db):
    """Test string input for slots raises ValidationError"""
    with pytest.raises(ValueError, match="Invalid job slots value"):
        # Note: Type checker would catch this, but testing runtime protection
        node_service.set_job_slots("node1", "five")  # type: ignore
    mock_db.update_node.assert_not_called()