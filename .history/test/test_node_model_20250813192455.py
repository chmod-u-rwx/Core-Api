import pytest
from pydantic import ValidationError
from src.core_api.models.node import Node

def test_node_creation(): #id and slot validation
    node = Node(node_id="node1", job_slots=3)
    assert node.node_id == "node1"
    assert node.job_slots == 3

def test_missing_node_id_raises_error():
    """Test that node_id is required"""
    with pytest.raises(ValidationError):
        Node(job_slots=3)  # Missing node_id

def test_no_job_slots():
    with pytest.raises(ValidationError):
        Node(node_id="N1")  # Missing job_slots

def test_emplty_node_id_():
    with pytest.raises(ValidationError):
        Node(node_id="", job_slots=4)

def test_job_slots_content():
    Node(node_id="node1", job_slots=1)
