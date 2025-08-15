import pytest
from unittest.mock import MagicMock, create_autospec
from typing import Optional
from pydantic import ValidationError
from src.core_api.services.node_service import NodeService
from src.core_api.models.node import Node

@pytest.fixture
def mock_db() -> MagicMock:
    mock = create_autospec(NodeDatabase)
    mock.update_node.return_value = None
    return mock
    # mocked database

@pytest.fixture
def service(mock_db: MagicMock) -> NodeService:
    return NodeService(mock_db)

def test_set_valid_job_slots(service: NodeService, mock_db: MagicMock):
    """Test successful job slot update"""
    expected_node = Node(node_id="node1", job_slots=3)
    mock_db.update_node.return_value = expected_node
    
    result = service.set_job_slots("node1", 3)

    assert result == expected_node
    mock_db.update_node.assert_called_once_with("node1", {"job_slots": 3})

def test_set_zero_job_slots(service: NodeService, mock_db: MagicMock):
    """Test zero is a valid slot count"""
    test_node = Node(node_id="node1", job_slots=0)
    mock_db.update_node.return_value = test_node
    
    result = service.set_job_slots("node1", 0)
    assert result.job_slots == 0

def test_negative_job_slots(service: NodeService, mock_db: MagicMock):
    """Test negative slots raise ValueError"""
    with pytest.raises(ValueError, match="cannot be empty"):
        service.set_job_slots("node1", -1)
    mock_db.update_node.assert_not_called()

def test_empty_node_id(service: NodeService, mock_db: MagicMock):
    """Test empty node_id raises ValidationError"""
    with pytest.raises(ValueError, match="Invalid job slots value"):
        service.set_job_slots("", 5)
    mock_db.update_node.assert_not_called()

def test_nonexistent_node(service: NodeService, mock_db: MagicMock):
    """Test non-existent node returns None"""
    mock_db.update_node.return_value = None
    assert service.set_job_slots("ghost", 2) is None
    mock_db.update_node.assert_called_once_with("ghost", {"job_slots": 2})


def test_string_slots_parameter(service: NodeService, mock_db: MagicMock):
    """Test string slot parameter raises ValidationError"""
    with pytest.raises(ValueError, match="Invalid job slots value"):
        service.set_job_slots("node1", "invalid")  # type: ignore
    mock_db.update_node.assert_not_called()

def test_none_slots_parameter(service: NodeService, mock_db: MagicMock):
    """Test None slot parameter raises ValidationError"""
    with pytest.raises(ValueError, match="Invalid job slots value"):
        service.set_job_slots("node1", None)  # type: ignore
    mock_db.update_node.assert_not_called()