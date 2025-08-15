import pytest
from pydantic import ValidationError
from src.core_api.models.node import Node

def test_node_creation():
    node = Node(node_id="node_1", job_slots=3)
    assert node.node_id == "node_1"
    assert node.job_slots == 3  # Id and slot validation