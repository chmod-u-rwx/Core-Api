import pytest
from pydantic import ValidationError
from src.core_api.models.node import Node

def test_node_creation():
    node = Node(node_id="node1", job_slots=3)
    assert node.node_id == "node1"
    assert node.job_slots == 3

def test_missing_node_id_raises_error():
    """Test that node_id is required"""
    with pytest.raises(ValidationError):
        Node(job_slots=3)  # Missing node_id

def test_no_job_slots():
    """Test that job_slots is required"""
    with pytest.raises(ValidationError):
        Node(node_id="N1")  # Missing job_slots

def test_emplty_node_id_():
    """Test node_id cannot be an empty string"""
    with pytest.raises(ValidationError):
        Node(node_id="", job_slots=4)

def test_job_slots_must_be_positive():
    """Test job_slots must be > 0"""
    Node(node_id="node1", job_slots=1)
