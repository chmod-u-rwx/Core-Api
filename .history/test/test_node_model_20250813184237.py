import pytest
from src.core_api.models.node import Node
from pydantic import ValidationError 

def test_valid_node_creation():
    """Test successful creation with valid data"""
    node = Node(node_id="node1", job_slots=4)
    assert node.node_id == "node1"
    assert node.job_slots == 4

def test_missing_node_id_raises_error():
    """Test that node_id is required"""
    with pytest.raises(ValidationError):
        Node(job_slots=4)  # Missing node_id

def test_missing_job_slots_raises_error():
    """Test that job_slots is required"""
    with pytest.raises(ValidationError):
        Node(node_id="node1")  # Missing job_slots

