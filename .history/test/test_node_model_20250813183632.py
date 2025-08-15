import pytest
from src.models.node import Node

import pytest
from models.node import Node


def test_node_creation():
    """Test basic node creation with required fields"""
    node = Node(node_id="node1", job_slots=4)
    
    assert node.node_id == "node1"
    assert node.job_slots == 4


def test_node_job_slots_validation():
    """Test that job_slots must be positive"""
    with pytest.raises(ValueError):
        Node(node_id="node1", job_slots=0)
    
    with pytest.raises(ValueError):
        Node(node_id="node1", job_slots=-1)


def test_node_id_required():
    """Test that node_id is required"""
    with pytest.raises(ValueError):
        Node(job_slots=4)  # missing node_id


def test_node_defaults():
    """Test that all fields are required (no defaults)"""
    # This test will need to be updated if we add optional fields later
    with pytest.raises(ValueError):
        Node(node_id="node1")  # missing job_slots
    
    with pytest.raises(ValueError):
        Node(job_slots=4)  # missing node_id