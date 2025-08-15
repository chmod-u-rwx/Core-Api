import pytest
from pymongo import MongoClient
from src.core_api


def test_set_job_slots_success():
    service = NodeService()
    result = service.set_job_slots("node1", 5)
    assert result is True
    assert service.node_slots["node1"] == 5

def test_set_job_slots_non_integer():
    service = NodeService()
    with pytest.raises(ValueError) as excinfo:
        service.set_job_slots("node1", "five")
    assert "integer" in str(excinfo.value)

def test_set_job_slots_negative_value():
    service = NodeService()
    with pytest.raises(ValueError) as excinfo:
        service.set_job_slots("node1", -3)
    assert "non-negative" in str(excinfo.value)
