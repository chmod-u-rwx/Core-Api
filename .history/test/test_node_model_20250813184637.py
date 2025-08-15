import pytest
from src.core_api.models.node import Node
from pydantic import ValidationError 
from pydantic 

def test_valid_node_creation():
    """Test successful creation with valid data"""
    node = Node(node_id="node1", job_slots=3)
    assert node.node_id == "node1"
    assert node.job_slots == 3

def test_missing_node_id_raises_error():
    """Test that node_id is required"""
    with pytest.raises(ValidationError):
        Node(job_slots=4)  # Missing node_id

def test_missing_job_slots_raises_error():
    """Test that job_slots is required"""
    with pytest.raises(ValidationError):
        Node(node_id="N1")  # Missing job_slots

def test_node_id_cannot_be_empty():
    """Test node_id cannot be an empty string"""
    with pytest.raises(ValidationError):
        Node(node_id="", job_slots=4)

def test_job_slots_must_be_positive():
    """Test job_slots must be > 0"""
    # Valid cases
    Node(node_id="node1", job_slots=1)  # Should pass
    # Invalid cases
    with pytest.raises(ValidationError):
        Node(node_id="node1", job_slots=0)
    with pytest.raises(ValidationError):
        Node(node_id="node1", job_slots=-5)