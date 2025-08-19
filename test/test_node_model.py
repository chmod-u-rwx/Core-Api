import pytest
from pydantic import ValidationError
from src.core_api.models.node_model import Node
from uuid import uuid4

def test_node_creation():
    uid = uuid4()
    node = Node(node_id=uid, job_slots=3, cpu_count=1, memory_allocated=1)
    assert node.node_id == uid
    assert node.job_slots == 3
    assert node.cpu_count == 1
    assert node.memory_allocated == 1

def test_missing_node_id_raises_error():
    with pytest.raises(ValidationError):
        Node(job_slots=3, cpu_count=1, memory_allocated=1)

def test_no_job_slots():
    with pytest.raises(ValidationError):
        Node(node_id=uuid4(), cpu_count=1, memory_allocated=1) 

def test_invalid_uuid_string():
    with pytest.raises(ValidationError):
        Node(node_id="not-a-uuid", job_slots=4, cpu_count=1, memory_allocated=1) 

def test_empty_node_id_():
    with pytest.raises(ValidationError):
        Node(node_id="", job_slots=4, cpu_count=1, memory_allocated=1)

def test_cpu_count_less_minimum():
    with pytest.raises(ValidationError):
        Node(node_id=uuid4(), job_slots=4, cpu_count=0, memory_allocated=1)

def test_memory_allocation_less_minimum():
    with pytest.raises(ValidationError):
        Node(node_id=uuid4(), job_slots=4, cpu_count=1, memory_allocated=0)

    
