import pytest
from pydantic import ValidationError
from src.core_api.models.node import Node

def test_valid_node_creation():
    node = Node(node_id="node1", job_slots=3)
    assert node.node_id == "node1"
    assert node.job_slots == 3

def test_missing_node_id_raises_error():
    with pytest.raises(ValidationError):
        Node(job_slots=4)

def test_missing_job_slots_raises_error():
    with pytest.raises(ValidationError):
        Node(node_id="N1")

def test_node_id_cannot_be_empty():
    with pytest.raises(ValidationError):
        Node(node_id="", job_slots=4)

def test_job_slots_must_be_positive():
    with pytest.raises(ValidationError):
        Node(node_id="node1", job_slots=0)
    with pytest.raises(ValidationError):
        Node(node_id="node1", job_slots=-5)
