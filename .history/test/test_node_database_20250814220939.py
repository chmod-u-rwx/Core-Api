import pytest
from mongomock import MongoClient
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from pymongo import MongoClient

class Node(BaseModel):
    node_id: str = Field(..., min_length=1)
    job_slots: int = Field(..., ge=0)

class NodeDatabase:
    def __init__(self, collection):
        self.collection = collection
        self.collection.create_index("node_id", unique=True)

    def create_node(self, data: dict) -> Node:
        node = Node(**data)
        try:
            self.collection.insert_one(node.model_dump())
            return node
        except DuplicateKeyError:
            raise ValueError("Node already exists")

    def get_node(self, node_id: str) -> Optional[Node]:
        doc = self.collection.find_one({"node_id": node_id})
        return Node(**doc) if doc else None
    
    def update_node(self, node_id: str, update_data: dict) -> Optional[Node]:
        result = self.collection.find_one_and_update(
            {"node_id": node_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        return Node(**result) if result else None

    def delete_node(self, node_id: str) -> bool:
        result = self.collection.delete_one({"node_id": node_id})
        return result.deleted_count > 0

# --- Fixtures ---
@pytest.fixture
def node_db():
    client = MongoClient()
    db = client["test_db"]
    return NodeDatabase(db["nodes"])

def test_create_and_get(node_database):
    node = node_db.create_node({"node_id": "n1", "job_slots": 2})
    assert node.node_id == "n1"
    fetched = node_db.get_node("n1")
    assert fetched == node

def test_duplicate(node_db):
    node_db.create_node({"node_id": "n1", "job_slots": 2})
    with pytest.raises(ValueError):
        node_db.create_node({"node_id": "n1", "job_slots": 5})

def test_get_nonexistent(node_db):
    assert node_db.get_node("missing") is None

def test_invalid_data(node_db):
    with pytest.raises(ValidationError):
        Node(node_id="x", job_slots=-1)

def test_update_node(node_db):
    node_db.create_node({"node_id": "n1", "job_slots": 2})
    updated = node_db.update_node("n1", {"job_slots": 5})
    assert updated.job_slots == 5
    assert node_db.get_node("n1").job_slots == 5

def test_update_nonexistent(node_db):
    assert node_db.update_node("missing", {"job_slots": 5}) is None

def test_delete_node(node_db):
    node_db.create_node({"node_id": "n1", "job_slots": 2})
    assert node_db.delete_node("n1") is True
    assert node_db.get_node("n1") is None

def test_delete_nonexistent(node_db):
    assert node_db.delete_node("missing") is False

def test_empty_node_id(node_db):
    with pytest.raises(ValidationError):
        node_db.create_node({"node_id": "", "job_slots": 1})

def test_negative_job_slots(node_db):
    with pytest.raises(ValidationError):
        node_db.create_node({"node_id": "n1", "job_slots": -1})