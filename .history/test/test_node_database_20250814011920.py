import pytest
import mongomock
from models.node import Node
from db.node_database import NodeDatabase

# ---- Fixture to inject mongomock ----
@pytest.fixture
def mock_node_db(monkeypatch):
    # Patch MongoClient to use mongomock
    import pymongo
    monkeypatch.setattr(pymongo, "MongoClient", mongomock.MongoClient)

    # Create instance
    db = NodeDatabase()
    db.collection = db.client["test_db"]["nodes"]  # force test collection
    yield db
    db.close()

# ---- Sample data ----
sample_node_data = {
    "node_id": "n1",
    "name": "Test Node",
    "ip": "192.168.0.10",
    "status": "active"
}

def test_create_node_success(mock_node_db):
    node = mock_node_db.create_node(sample_node_data)
    assert isinstance(node, Node)
    assert node.node_id == "n1"
    assert mock_node_db.count_nodes() == 1

def test_create_node_duplicate(mock_node_db):
    mock_node_db.create_node(sample_node_data)
    with pytest.raises(ValueError):
        mock_node_db.create_node(sample_node_data)

def test_get_node(mock_node_db):
    mock_node_db.create_node(sample_node_data)
    node = mock_node_db.get_node("n1")
    assert node is not None
    assert node.node_id == "n1"

def test_update_node(mock_node_db):
    mock_node_db.create_node(sample_node_data)
    updated = mock_node_db.update_node("n1", {"status": "inactive"})
    assert updated.status == "inactive"

def test_delete_node(mock_node_db):
    mock_node_db.create_node(sample_node_data)
    assert mock_node_db.delete_node("n1") is True
    assert mock_node_db.count_nodes() == 0

def test_node_exists(mock_node_db):
    mock_node_db.create_node(sample_node_data)
    assert mock_node_db.node_exists("n1") is True
    assert mock_node_db.node_exists("n2") is False

def test_get_all_nodes(mock_node_db):
    mock_node_db.create_node(sample_node_data)
    mock_node_db.create_node({"node_id": "n2", "name": "Node 2", "ip": "192.168.0.11", "status": "active"})
    nodes = mock_node_db.get_all_nodes()
    assert len(nodes) == 2
