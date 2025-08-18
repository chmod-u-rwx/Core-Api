import pytest
from pydantic import ValidationError
from uuid import uuid4
from mongomock import MongoClient
import mongomock
from src.core_api.db.node_database import NodeDatabase
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

def test_create_and_get(node_db: NodeDatabase):
    node = node_db.create_node(Node(node_id=uuid4(), job_slots=2))
    fetched = node_db.get_node(node.node_id)
    assert fetched == node

def test_duplicate(node_db: NodeDatabase):
    node = node_db.create_node(Node(node_id=uuid4(), job_slots=2))
    with pytest.raises(ValueError, match="already exists"):
        node_db.create_node(Node(node_id=node.node_id, job_slots=2))

def test_get_nonexistent(node_db: NodeDatabase):
    with pytest.raises(ValueError, match="does not exist"):
        node_db.get_node(uuid4())

def test_invalid_data(node_db: NodeDatabase):
    # only negative values should fail
    with pytest.raises(ValidationError):
        Node(node_id=uuid4(), job_slots=-1)

def test_update_node(node_db: NodeDatabase):
    node = node_db.create_node(Node(node_id=uuid4(), job_slots=2))
    updated = node_db.update_node(node.node_id, NodeUpdates(job_slots=5))
    assert updated.job_slots == 5
    assert node_db.get_node(node.node_id).job_slots == 5

def test_update_nonexistent(node_db: NodeDatabase):
    with pytest.raises(ValueError, match="does not exist"):
        node_db.update_node(uuid4(), NodeUpdates(job_slots=5))

def test_delete_node(node_db: NodeDatabase):
    node = node_db.create_node(Node(node_id=uuid4(), job_slots=2))
    assert node_db.delete_node(node.node_id) is True
    with pytest.raises(ValueError, match="does not exist"):
        node_db.get_node(node.node_id)

def test_delete_nonexistent(node_db: NodeDatabase):
    assert node_db.delete_node(uuid4()) is False