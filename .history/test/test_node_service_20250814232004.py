
import pytest
from unittest.mock import MagicMock, create_autospec
from typing import Optional
from pydantic import ValidationError
from src.core_api.db.node_database import NodeDatabase
from src.core_api.models.node import Node
from src.core_api.services.node_service import NodeService

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
    
