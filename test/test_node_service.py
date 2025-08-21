import pytest
from uuid import uuid4
from mongomock import MongoClient
import mongomock
from src.core_api.db.node_database import NodeDatabase
from src.core_api.services.node_service import NodeService
from src.core_api.models.node_model import Node, NodeUpdates
from typing import Any
from unittest.mock import patch

@pytest.fixture
def node_db():
    with patch("src.core_api.db.node_database.get_mongo_client") as mock_mongo_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_mongo_client.return_value = mock_client
        db = NodeDatabase()

        yield db

@pytest.fixture
def service(node_db: NodeDatabase):
    return NodeService(node_db)

def test_node_update_success(service: NodeService, node_db: NodeDatabase):
    node = node_db.create_node(Node(node_id=uuid4(), job_slots=5, cpu_count=1, memory_allocated=1))
    assert node.job_slots == 5
    updated = service.update_node(node.node_id, NodeUpdates(job_slots=2, cpu_count=2, memory_allocated=2))
    assert updated.job_slots == 2
    assert node_db.get_node(node.node_id).job_slots == 2

def test_set_job_slots_less_than_zero(service: NodeService, node_db: NodeDatabase):
    node = node_db.create_node(Node(node_id=uuid4(), job_slots=2, cpu_count=1, memory_allocated=1))
    with pytest.raises(Exception, match="Input should be greater than or equal to 0"):
        service.update_node(node.node_id, NodeUpdates(job_slots=-1))

def test_set_job_slots_nonexistent_node(service: NodeService):
    with pytest.raises(KeyError):
        service.update_node(uuid4(), NodeUpdates(job_slots=1))
