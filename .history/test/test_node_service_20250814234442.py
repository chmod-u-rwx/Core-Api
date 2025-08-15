import pytest
from unittest.mock import MagicMock
from src.core_api.services.node_service import NodeService
from src.core_api.models.node import Node


@pytest.fixture
def mock_node_db():
    """Fixture for mocking NodeDatabase."""
    return MagicMock()


@pytest.fixture
def node_service(mock_node_db):
    """Fixture for creating NodeService with mocked DB."""
    return NodeService(node_db=mock_node_db)


def test_set_job_slots_success(node_service, mock_node_db):
    # Arrange
    node_id = "node123"
    slots = 5
    expected_node = Node(node_id=node_id, job_slots=slots)
    mock_node_db.update_node.return_value = expected_node

    # Act
    result = node_service.set_job_slots(node_id, slots)

    # Assert
    mock_node_db.update_node.assert_called_once_with(node_id, {"job_slots": slots})
    assert result == expected_node


def test_set_job_slots_invalid_type(node_service):
    with pytest.raises(ValueError) as excinfo:
        node_service.set_job_slots("node123", "five")
    assert "Job slots must be an integer" in str(excinfo.value)


def test_set_job_slots_negative_value(node_service):
    with pytest.raises(ValueError) as excinfo:
        node_service.set_job_slots("node123", -3)
    assert "Job slots cannot be negative" in str(excinfo.value)


def test_set_job_slots_pydantic_validation_error(node_service, mock_node_db):
    # Force Pydantic validation error by mocking Node model
    from pydantic import ValidationError
    import src.core_api.services.node_service as node_service_module

    def raise_validation_error(*args, **kwargs):
        raise ValidationError([], Node)

    node_service_module.Node = raise_validation_error

    with pytest.raises(ValueError) as excinfo:
        node_service.set_job_slots("node123", 2)

    assert "Invalid job slots value" in str(excinfo.value)
