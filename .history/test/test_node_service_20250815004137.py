import sys
import os

# Make sure Python can find "src"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core_api.services.node_service import NodeService


def test_set_job_slots_success():
    service = NodeService()
    result = service.set_job_slots("node1", 5)
    assert result is True
    assert service.node_slots["node1"] == 5


def test_set_job_slots_non_integer():
    import pytest
    service = NodeService()
    with pytest.raises(ValueError, match="integer"):
        service.set_job_slots("node1", "five")


def test_set_job_slots_negative_value():
    import pytest
    service = NodeService()
    with pytest.raises(ValueError, match="non-negative"):
        service.set_job_slots("node1", -3)
