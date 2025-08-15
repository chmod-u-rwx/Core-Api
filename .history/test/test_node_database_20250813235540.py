import pytest
from pymongo import MongoClient
from src.core_api.models.node import Node
from src.core_api.db.node_database import NodeDatabase
from pymongo.errors import DuplicateKeyError

@pytest.fixture
def test_db():
    """Fixture that provides a test database instance"""
    db = NodeDatabase()
    yield db
    # Cleanup after tests
    db.collection.delete_many({})
    db.close()

@pytest.fixture
def sample_node_data():
    return {"node_id": "test_node", "job_slots": 4}

def test_connection(test_db):
    """Test database connection is established"""
    assert test_db.client is not None
    assert test_db.node_database == "test"  # Assuming test database

def test_create_node(test_db, sample_node_data):
    """Test node creation"""
    node = test_db.create_node(sample_node_data)
    assert isinstance(node, Node)
    assert node.node_id == "test_node"
    assert node.job_slots == 4

def test_create_duplicate_node(test_db, sample_node_data):
    """Test duplicate node creation fails"""
    test_db.create_node(sample_node_data)
    with pytest.raises(ValueError, match="already exists"):
        test_db.create_node(sample_node_data)

def test_get_node(test_db, sample_node_data):
    """Test retrieving a node"""
    test_db.create_node(sample_node_data)
    node = test_db.get_node("test_node")
    assert node is not None
    assert node.node_id == "test_node"

def test_get_nonexistent_node(test_db):
    """Test retrieving non-existent node"""
    assert test_db.get_node("nonexistent") is None

def test_get_all_nodes(test_db, sample_node_data):
    """Test retrieving all nodes"""
    test_db.create_node(sample_node_data)
    test_db.create_node({"node_id": "node2", "job_slots": 2})
    
    nodes = test_db.get_all_nodes()
    assert len(nodes) == 2
    assert {n.node_id for n in nodes} == {"test_node", "node2"}

def test_update_node(test_db, sample_node_data):
    """Test updating a node"""
    test_db.create_node(sample_node_data)
    
    # Update job_slots
    updated_node = test_db.update_node("test_node", {"job_slots": 8})
    assert updated_node is not None
    assert updated_node.job_slots == 8
    
    # Verify update persisted
    node = test_db.get_node("test_node")
    assert node.job_slots == 8

def test_update_nonexistent_node(test_db):
    """Test updating non-existent node"""
    assert test_db.update_node("nonexistent", {"job_slots": 8}) is None

def test_delete_node(test_db, sample_node_data):
    """Test deleting a node"""
    test_db.create_node(sample_node_data)
    assert test_db.delete_node("test_node") is True
    assert test_db.get_node("test_node") is None

def test_delete_nonexistent_node(test_db):
    """Test deleting non-existent node"""
    assert test_db.delete_node("nonexistent") is False

def test_node_exists(test_db, sample_node_data):
    """Test node existence check"""
    assert test_db.node_exists("test_node") is False
    test_db.create_node(sample_node_data)
    assert test_db.node_exists("test_node") is True

def test_count_nodes(test_db, sample_node_data):
    """Test node counting"""
    assert test_db.count_nodes() == 0
    test_db.create_node(sample_node_data)
    assert test_db.count_nodes() == 1
    test_db.create_node({"node_id": "node2", "job_slots": 2})
    assert test_db.count_nodes() == 2

def test_error_handling(test_db, sample_node_data, monkeypatch):
    """Test error handling scenarios"""
    # Simulate connection error
    def mock_find_one(*args, **kwargs):
        raise PyMongoError("Simulated database error")
    
    monkeypatch.setattr(test_db.collection, "find_one", mock_find_one)
    with pytest.raises(RuntimeError, match="Database operation failed"):
        test_db.get_node("test_node")

    # Test invalid data handling
    with pytest.raises(ValueError):
        test_db.create_node({"node_id": "test_node", "job_slots": -1})

def test_cleanup(test_db, sample_node_data):
    """Test database cleanup"""
    test_db.create_node(sample_node_data)
    test_db.collection.delete_many({})
    assert test_db.count_nodes() == 0