import pytest
from uuid import uuid4
from mongomock import MongoClient
from src.core_api.db.node_database import NodeDatabase
from src.core_api.services.node_service import NodeService

@pytest.fixture
def node_db():
    client = MongoClient()
    db = client["test_db"]
    return NodeDatabase(db["nodes"])

@pytest.fixture
def node_service(node_db):
    return NodeService(node_db)

def test_set_job_slots_success(node_service, node_db):
    node_id = uuid4()
    node_db.create_node({"node_id": node_id, "job_slots": 2})
    updated_node = node_service.set_job_slots(node_id, 5)
    assert updated_node.job_slots == 5

def test_set_job_slots_negative(node_service, node_db):
    node_id = uuid4()
    node_db.create_node({"node_id": node_id, "job_slots": 2})
    with pytest.raises(ValueError):
        node_service.set_job_slots(node_id, -1)

def test_set_job_slots_nonexistent(node_service):
    from uuid import uuid4
    node_id = uuid4()
    result = node_service.set_job_slots(node_id, 3)
    assert result is None
