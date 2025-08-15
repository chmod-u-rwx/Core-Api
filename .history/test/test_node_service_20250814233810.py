# tests/services/test_node_service.py
import pytest
from unittest.mock import MagicMock
from core_api.services.node_service import NodeService

def test_set_job_slots_valid():
    mock_db = MagicMock()
    mock_db.update_node.return_value = {"node_id": "abc123", "job_slots": 5}

    service = NodeService(mock_db)
    result = service.set_job_slots("abc123", 5)

    mock_db.update_node.assert_called_once_with("abc123", {"job_slots": 5})
    assert result["job_slots"] == 5

def test_set_job_slots_negative():
    mock_db = MagicMock()
    service = NodeService(mock_db)

    with pytest.raises(ValueError) as e:
        service.set_job_slots("abc123", -1)

    assert "Job slots cannot be empty" in str(e.value)
