import pytest
from uuid import uuid4
from src.core_api.db.node_database import NodeDatabase
from src.core_api.services.node_service import NodeService
from src.core_api.models.node_model import Node

@pytest.fixture
def node_db():
    return NodeDatabase()

@pytest.fixture
def service(node_db):
    return NodeService(node_db)

def test_set_job_slots_inserted(service, node_db):
    node = node_db.create_node(Node(node_id=uuid4(), job_slots=5))
    updated = service.set_job_slots(node.node_id, 5)
    assert updated.job_slots == 5
    assert node_db.get_node(node.node_id).job_slots == 5

def test_set_job_slots_less_than_zero(service, node_db):
    node = node_db.create_node(Node(node_id=uuid4(), job_slots=2))
    with pytest.raises(ValueError, match="job_slots must be >= 0"):
        service.set_job_slots(node.node_id, -1)

def test_set_job_slots_nonexistent_node(service):
    with pytest.raises(ValueError):
        service.set_job_slots(uuid4(), 5)
