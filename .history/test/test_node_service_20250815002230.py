import pytest
from unittest.mock import create_autospec

# ✅ Explicit imports so no NameError
from src.core_api.db.node_database import NodeDatabase
from src.core_api.services.node_service import NodeService


@pytest.fixture
def mock_db():
    """Fixture providing a strict mock of NodeDatabase."""
    return create_autospec(NodeDatabase)


def test_set_job_slots_success(mock_db):
    """Test setting job slots with a valid integer value."""
    service = NodeService(mock_db)
    service.set_job_slots("node-123", 5)

    mock_db.set_job_slots.assert_called_once_with("node-123", 5)


def test_set_job_slots_non_integer(mock_db):
    """Test that a non-integer slots value raises ValueError."""
    service = NodeService(mock_db)

    with pytest.raises(ValueError, match="Slots must be an integer"):
        service.set_job_slots("node-123", "five")  # ❌ Not an int


def test_set_job_slots_negative(mock_db):
    """Test that a negative slots value raises ValueError."""
    service = NodeService(mock_db)

    with pytest.raises(ValueError, match="Slots must be non-negative"):
        service.set_job_slots("node-123", -1)
