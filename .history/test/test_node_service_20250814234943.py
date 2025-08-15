import pytest
import mongomock
from unittest.mock import create_autospec
from pydantic import ValidationError
from
from src.core_api.models.node import Node

@pytest.fixture
def mock_db():
    """Fixture providing a mock NodeDatabase"""
    mock = create_autospec('NodeDatabase')  # Strict mock that validates calls
    mock.update_node.return_value = None  # Default return value
    return mock

@pytest.fixture
def node_service(mock_db):
    """Fixture providing a NodeService with mocked database"""
    return NodeService(mock_db)

# ---- Success Cases ----
def test_set_job_slots_success(node_service, mock_db):
    """Test successful job slot update with valid input"""
    # Setup
    test_node = Node(node_id="node1", job_slots=5)
    mock_db.update_node.return_value = test_node