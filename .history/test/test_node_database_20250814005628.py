import pytest
from mongomock import MongoClient
from pymongo.errors import DuplicateKeyError
from src.core_api.db.node_database import NodeDatabase
from src.core_api.models.node import Node

@pytest.fixture
def mock_mongo():
    """Fixture that provides a mongomock client"""
    return MongoClient()

@pytest.fixture
def test_db(mock_mongo):
    """Fixture that provides a properly configured NodeDatabase with mongomock"""
    db = NodeDatabase()
    
    # Override the real MongoDB client with mongomock
    db.client = mock_mongo
    db.db = mock_mongo.get_database("test_db")
    db.collection = db.db["nodes"]
    
    # Ensure indexes exist (mongomock supports basic index functionality)
    db.collection.create_index("node_id", unique=True)
    
    yield db
    
    # Cleanup (though mongomock is in-memory, this clears between tests)
    db.collection.delete_many({})

@pytest.fixture
def sample_node():
    return {"node_id": "test_node", "job_slots": 4}

def test_create_node(test_db, sample_node):
    """Test node creation matches NodeDatabase implementation"""
    node = test_db.create_node(sample_node)
    assert isinstance(node, Node)
    assert node.node_id == "test_node"
    assert node.job_slots == 4
    
    # Verify it was actually inserted
    assert test_db.collection.count_documents({"node_id": "test_node"}) == 1

def test_duplicate_node_creation(test_db, sample_node):
    """Test duplicate prevention matches your error handling"""
    test_db.create_node(sample_node)
    with pytest.raises(ValueError, match="already exists"):
        test_db.create_node(sample_node)

def test_get_node(test_db, sample_node):
    """Test retrieval matches your implementation"""
    test_db.create_node(sample_node)
    node = test_db.get_node("test_node")
    assert node.node_id == "test_node"
    assert node.job_slots == 4

def test_get_nonexistent_node(test_db):
    """Test your None return for missing nodes"""
    assert test_db.get_node("nonexistent") is None

def test_update_node(test_db, sample_node):
    """Test your update logic"""
    test_db.create_node(sample_node)
    updated = test_db.update_node("test_node", {"job_slots": 8})
    assert updated.job_slots == 8
    assert test_db.get_node("test_node").job_slots == 8

def test_delete_node(test_db, sample_node):
    """Test your delete implementation"""
    test_db.create_node(sample_node)
    assert test_db.delete_node("test_node") is True
    assert test_db.get_node("test_node") is None

def test_node_exists(test_db, sample_node):
    """Test your existence check"""
    assert test_db.node_exists("test_node") is False
    test_db.create_node(sample_node)
    assert test_db.node_exists("test_node") is True

def test_count_nodes(test_db):
    """Test your counting implementation"""
    assert test_db.count_nodes() == 0
    test_db.create_node({"node_id": "node1", "job_slots": 1})
    assert test_db.count_nodes() == 1
    test_db.create_node({"node_id": "node2", "job_slots": 2})
    assert test_db.count_nodes() == 2

def test_invalid_data_handling(test_db):
    """Test your validation error handling"""
    with pytest.raises(ValueError):
        test_db.create_node({"node_id": "", "job_slots": 1})  # Empty node_id
    with pytest.raises(ValueError):
        test_db.create_node({"node_id": "node1", "job_slots": -1})  # Negative slots