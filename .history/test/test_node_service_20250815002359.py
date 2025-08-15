import pytest
from unittest.mock import create_autospec
from pydantic import ValidationError




@pytest.fixture
def mock_db():
    """Fixture providing a strict mock of NodeDatabase."""
    mock = create_autospec(NodeDatabase)  # ✅ Pass the actual class, not a string
    return mock


@pytest.fixture
def node_service(mock_db):
    """Fixture providing NodeService with mocked DB."""
    return NodeService(node_db=mock_db)


def test_set_job_slots_success(mock_db, node_service):
    node_id = "node123"
    slots = 5
    expected_node = Node(node_id=node_id, job_slots=slots)

    mock_db.update_node.return_value = expected_node

    result = node_service.set_job_slots(node_id, slots)

    mock_db.update_node.assert_called_once_with(node_id, {"job_slots": slots})
    assert result == expected_node


def test_set_job_slots_non_integer(node_service):
    node_id = "node123"
    slots = "five"

    with pytest.raises(ValueError, match="Job slots must be an integer"):
        node_service.set_job_slots(node_id, slots)


def test_set_job_slots_negative_value(node_service):
    node_id = "node123"
    slots = -1

    with pytest.raises(ValueError, match="Job slots cannot be negative"):
        node_service.set_job_slots(node_id, slots)


def test_set_job_slots_validation_error(mock_db):
    service = NodeService(node_db=mock_db)
    node_id = "node123"
    slots = 10

    # Force Pydantic to fail by mocking Node to raise ValidationError
    def bad_node_init(*args, **kwargs):
        raise ValidationError([], Node)

    import src.core_api.services.node_service as ns
    original_node = ns.Node
    ns.Node = bad_node_init

    try:
        with pytest.raises(ValueError, match="Invalid job slots value"):
            service.set_job_slots(node_id, slots)
    finally:
        ns.Node = original_node
