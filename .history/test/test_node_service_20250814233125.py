import pytest
from pydantic import ValidationError
from src.core_api.services.node_service import NodeService

import pytest
from unittest.mock import MagicMock, patch
import logging
from pydantic import ValidationError
from models.node import Node
from services.node_service import NodeService

@pytest.fixture
def mock_db():
    """Fixture providing a mock NodeDatabase"""
    return MagicMock()

@pytest.fixture
def node_service(mock_db):
    """Fixture providing a NodeService with mocked database"""
    service = NodeService(mock_db)
    # Capture logs for verification
    service.logger = MagicMock()
    return service

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
    node_service.logger.info.assert_called_once_with(
        "Successfully updated node node1 slots to 5"
    )

# ---- Validation Error Cases ----
def test_negative_job_slots(node_service, mock_db):
    """Test negative slots raise error"""
    with pytest.raises(ValueError, match="cannot be negative"):
        node_service.set_job_slots("node1", -1)
    mock_db.update_node.assert_not_called()
    node_service.logger.error.assert_called_once()

def test_non_integer_slots(node_service, mock_db):
    """Test non-integer slots raise error"""
    with pytest.raises(ValueError, match="must be an integer"):
        node_service.set_job_slots("node1", "five")  # type: ignore
    mock_db.update_node.assert_not_called()

def test_empty_node_id(node_service, mock_db):
    """Test empty node ID raises validation error"""
    with pytest.raises(ValueError):
        node_service.set_job_slots("", 5)
    mock_db.update_node.assert_not_called()

# ---- Database Interaction Cases ----
def test_nonexistent_node(node_service, mock_db):
    """Test non-existent node returns None"""
    mock_db.update_node.return_value = None
    assert node_service.set_job_slots("ghost", 5) is None
    mock_db.update_node.assert_called_once_with("ghost", {"job_slots": 5})
    node_service.logger.warning.assert_called_once_with(
        "Node ghost not found"
    )

# ---- Edge Cases ----
def test_zero_job_slots(node_service, mock_db):
    """Test zero slots is allowed"""
    test_node = Node(node_id="node1", job_slots=0)
    mock_db.update_node.return_value = test_node
    
    result = node_service.set_job_slots("node1", 0)
    assert result.job_slots == 0
    mock_db.update_node.assert_called_once_with("node1", {"job_slots": 0})

def test_large_job_slots(node_service, mock_db):
    """Test large slot values are allowed"""
    test_node = Node(node_id="node1", job_slots=10000)
    mock_db.update_node.return_value = test_node
    
    result = node_service.set_job_slots("node1", 10000)
    assert result.job_slots == 10000

# ---- Logging Verification ----
def test_error_logging(node_service, mock_db):
    """Test errors are properly logged"""
    with pytest.raises(ValueError):
        node_service.set_job_slots("node1", -1)
    assert node_service.logger.error.called