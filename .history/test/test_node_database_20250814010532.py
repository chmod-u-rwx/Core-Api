import pytest
from mongomock import MongoClient
from src.core_api.models.node import Node
from src.core_api.db.node_database import NodeDatabase

# --- Fixtures ---
@pytest.fixture
def node_db():
    """Fixture to create an in-memory NodeDatabase using mongomock."""
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
    with pytest.raises(ValueError):
        Node(node_id="x", job_slots=-1)

def test_update_node(node_db):
    node_db.create_node({"node_id": "n1", "job_slots": 2})
    updated = node_db.update_node("n1", {"job_slots": 5})
    assert updated.job_slots == 5
    fetched = node_db.get_node("n1")
    assert fetched.job_slots == 5

def test_update_nonexistent(node_db):
    with pytest.raises(ValueError):
        node_db.update_node("missing", {"job_slots": 3})

def test_delete_node(node_db):
    node_db.create_node({"node_id": "n1", "job_slots": 2})
    assert node_db.delete_node("n1") is True
    assert node_db.get_node("n1") is None

def test_delete_nonexistent(node_db):
    assert node_db.delete_node("missing") is False
