import pytest
from mongomock import MongoClient
from pydantic import BaseModel, Field, ValidationError
from uuid import uuid4, UUID
from typing import Optional
from pymongo.errors import DuplicateKeyError
from src.core_api.db.node_database import NodeDatabase
from src.core_api.models.node_model import Node


@pytest.fixture
def node_db():
    client = MongoClient()
    db = client["test_db"]
    return NodeDatabase(db["Nodes"])

def test_create_and_get(node_db):
    node = node_db.create_node({"job_slots": 2})
    fetched = node_db.get_node(str(node.node_id))
    assert fetched == node

def test_duplicate(node_db):
    node = node_db.create_node({"job_slots": 2})
    with pytest.raises(ValueError):
        node_db.create_node({"node_id": str(node.node_id), "job_slots": 5})

def test_get_nonexistent(node_db):
        node_db.get_node(str(uuid4()))
        assert node_db.get_node(str(uuid4())) is None

def test_invalid_data(node_db):
    with pytest.raises(ValidationError):
        Node(node_id=uuid4(), job_slots=-1)

def test_update_node(node_db):
    node = node_db.create_node({"job_slots": 2})
    updated = node_db.update_node(str(node.node_id), {"job_slots": 5})
    assert updated.job_slots == 5
    assert node_db.get_node(str(node.node_id)).job_slots == 5

def test_update_nonexistent(node_db):
    assert node_db.update_node(str(uuid4()), {"job_slots": 5}) is None

def test_delete_node(node_db):
    node = node_db.create_node({"job_slots": 2})
    assert node_db.delete_node(str(node.node_id)) is True
    assert node_db.get_node(str(node.node_id)) is None

def test_delete_nonexistent(node_db):
    assert node_db.delete_node(str(uuid4())) is False

def test_negative_job_slots(node_db):
    with pytest.raises(ValidationError):
        node_db.create_node({"job_slots": -1})
