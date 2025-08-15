import pytest
from src.core_api.models.node import Node
from pydantic import ValidationError 

def test_valid_node_creation():
    """Test successful creation with valid data"""
    node = Node(node_id="node1", job_slots=4)
    assert node.node_id == "node1"
    assert node.job_slots == 4

