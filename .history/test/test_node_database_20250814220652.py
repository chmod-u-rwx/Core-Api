import pytest
from mongomock import MongoClient
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from pymongo import MongoClient
from src.core_api.db.node_database import NodeDatabase

# --- Node Model ---
class Node(BaseModel):
    node_id: str = Field(..., min_length=1)
    job_slots: int = Field(..., ge=0)

# --- Simple Node Database ---
def create_node(collection: Collection, data: dict) -> Node:
    """Lightweight create with validation and duplicate check"""
    try:
        node = Node(**data)
        collection.insert_one(node.model_dump())
        return node
    except (ValidationError, DuplicateKeyError) as e:
        raise ValueError(f"Invalid node: {str(e)}")

def get_node(collection: Collection, node_id: str) -> Optional[Node]:
    """Safe get with type conversion"""
    if doc := collection.find_one({"node_id": node_id}):
        return Node(**doc)
    return None

def ensure_index(collection: Collection):
    """One-time index setup"""
    collection.create_index("node_id", unique=True)

# --- Fixtures ---
@pytest.fixture
def node_db():
    client = MongoClient()
    db = client["test_db"]
    return NodeDatabase(db["nodes"])

# --- Tests ---
def test_create_and_get(node_db):
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