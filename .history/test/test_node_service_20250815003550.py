import pytest
from unittest.mock import MagicMock
from pymongo.errors import PyMongoError

# ✅ Explicit imports so no NameError
from src.core_api.services.node_service import NodeService
from src.core_api.models.node import Node

@pytest.fixture
def mock_node_db():
    return MagicMock()

@pytest.fixture
def node_service(mock_node_db):
    return NodeService(node_db=mock_node_db)

def test_set_job_slots_success(node_service, mock_node_db):
    node_id = "node123"
    slots = 5
    mock_node_db.update_job_slots.return_value = True

    result = node_service.set_job_slots(node_id, slots)

    mock_node_db.update_job_slots.assert_called_once_with(node_id, slots)
    assert result is True

def test_set_job_slots_non_integer(node_service):
    node_id = "node123"
    slots = "five"

    with pytest.raises(ValueError, match="Job slots must be an integer"):
        node_service.set_job_slots(node_id, slots)

def test_set_job_slots_negative_value(node_service):
    node_id = "node123"
    slots = -1

    with pytest.raises(ValueError, match="Job slots must be a non-negative integer"):
        node_service.set_job_slots(node_id, slots)

def test_set_job_slots_validation_error(node_service, mock_node_db):
    node_id = "node123"
    slots = 3
    mock_node_db.update_job_slots.side_effect = PyMongoError("Database error")

    with pytest.raises(PyMongoError, match="Database error"):
        node_service.set_job_slots(node_id, slots)
