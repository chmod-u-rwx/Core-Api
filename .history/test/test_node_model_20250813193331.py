import pytest
from pydantic import ValidationError
from src.core_api.models.node import Node

def test_node_creation():
    node = Node(node_id="node_1", job_slots=3)
    assert node.node_id == "node_1"
    assert node.job_slots == 3  # Id and slot validation

def test_missing_node_id_raises_error():
    with pytest.raises(ValidationError):
        Node(job_slots=3)  # Missing node_id

def test_no_job_slots():
    with pytest.raises(ValidationError):
        Node(node_id="N_1")  # Missing job_slots

def test_empty_node_id_():
    with pytest.raises(ValidationError):
        Node(node_id="", job_slots=4) # cant be an empty string
