import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import create_autospec
from pydantic import ValidationError
from src.core_api.models.node import Node
from src.core_api.services.node_service import NodeService

def test_set_job_slots_success(mock_db, node_service):
    # Arrange
    node_id = "node123"
    slots = 5
    expected_node = Node(node_id=node_id, job_slots=slots)

    mock_db.update_node.return_value = expected_node

    # Act
    result = node_service.set_job_slots(node_id, slots)

    # Assert
    mock_db.update_node.assert_called_once_with(node_id, {"job_slots": slots})
    assert result == expected_node


def test_set_job_slots_non_integer(node_service):
    # Arrange
    node_id = "node123"
    slots = "five"

    # Act & Assert
    with pytest.raises(ValueError, match="Job slots must be an integer"):
        node_service.set_job_slots(node_id, slots)


def test_set_job_slots_negative_value(node_service):
    # Arrange
    node_id = "node123"
    slots = -1

    # Act & Assert
    with pytest.raises(ValueError, match="Job slots cannot be negative"):
        node_service.set_job_slots(node_id, slots)


def test_set_job_slots_validation_error(mock_db):
    # Arrange
    service = NodeService(node_db=mock_db)
    node_id = "node123"
    slots = 10

    # Force Pydantic to fail by mocking Node to raise ValidationError
    def bad_node_init(*args, **kwargs):
        raise ValidationError([], Node)

    # Temporarily patch Node
    import src.core_api.services.node_service as ns
    original_node = ns.Node
    ns.Node = bad_node_init

    try:
        with pytest.raises(ValueError, match="Invalid job slots value"):
            service.set_job_slots(node_id, slots)
    finally:
        # Restore original Node
        ns.Node = original_node
