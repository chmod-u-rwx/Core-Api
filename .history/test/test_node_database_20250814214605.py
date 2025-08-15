import pytest
from unittest.mock import patch, MagicMock
from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError
from rcmodels.node import Node
from your_module import NodeDatabase  # Replace with your actual module path

# Test data
SAMPLE_NODE = {
    "node_id": "test_node_1",
    "name": "Test Node",
    "type": "sensor",
    "location": "room_101",
    "status": "active"
}

@pytest.fixture
def mock_mongo():
    with patch('pymongo.MongoClient') as mock:
        yield mock

@pytest.fixture
def node_db(mock_mongo):
    # Mock the database connection and collections
    mock_client = MagicMock(spec=MongoClient)
    mock_db = MagicMock()
    mock_collection = MagicMock()
    
    mock_mongo.return_value = mock_client
    mock_client.get_database.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    
    return NodeDatabase()

def test_get_client_success(mock_mongo):
    """Test successful MongoDB client connection"""
    mock_client = MagicMock()
    mock_mongo.return_value = mock_client
    mock_client.admin.command.return_value = True
    
    db = NodeDatabase()
    assert db.client == mock_client
    mock_client.admin.command.assert_called_once_with('ping')

def test_get_client_failure(mock_mongo):
    """Test MongoDB connection failure"""
    mock_mongo.side_effect = PyMongoError("Connection failed")
    
    with pytest.raises(RuntimeError, match="MongoDB failed connecting"):
        NodeDatabase()

def test_check_indexes(node_db):
    """Test index creation"""
    node_db._check_indexes()
    node_db.collection.create_index.assert_called_once_with("node_id", unique=True)

def test_check_indexes_failure(node_db):
    """Test index creation failure"""
    node_db.collection.create_index.side_effect = PyMongoError("Index error")
    
    with pytest.raises(RuntimeError, match="Index unresponsive"):
        node_db._check_indexes()

def test_create_node_success(node_db):
    """Test successful node creation"""
    mock_result = MagicMock()
    mock_result.acknowledged = True
    node_db.collection.insert_one.return_value = mock_result
    
    result = node_db.create_node(SAMPLE_NODE)
    assert isinstance(result, Node)
    node_db.collection.insert_one.assert_called_once()

def test_create_node_duplicate(node_db):
    """Test duplicate node creation"""
    node_db.collection.insert_one.side_effect = DuplicateKeyError("Duplicate")
    
    with pytest.raises(ValueError, match="already exists"):
        node_db.create_node(SAMPLE_NODE)

def test_create_node_failure(node_db):
    """Test node creation failure"""
    node_db.collection.insert_one.side_effect = PyMongoError("DB error")
    
    with pytest.raises(RuntimeError, match="Creating operation failed"):
        node_db.create_node(SAMPLE_NODE)

def test_get_node_success(node_db):
    """Test successful node retrieval"""
    node_db.collection.find_one.return_value = SAMPLE_NODE
    
    result = node_db.get_node("test_node_1")
    assert isinstance(result, Node)
    assert result.node_id == "test_node_1"
    node_db.collection.find_one.assert_called_once_with({"node_id": "test_node_1"})

def test_get_node_not_found(node_db):
    """Test node not found"""
    node_db.collection.find_one.return_value = None
    
    result = node_db.get_node("nonexistent_node")
    assert result is None

def test_get_node_failure(node_db):
    """Test node retrieval failure"""
    node_db.collection.find_one.side_effect = PyMongoError("DB error")
    
    with pytest.raises(RuntimeError, match="Database operation failed"):
        node_db.get_node("test_node_1")

def test_get_all_nodes_success(node_db):
    """Test successful retrieval of all nodes"""
    sample_nodes = [SAMPLE_NODE, {**SAMPLE_NODE, "node_id": "test_node_2"}]
    node_db.collection.find.return_value = sample_nodes
    
    result = node_db.get_all_nodes()
    assert len(result) == 2
    assert all(isinstance(node, Node) for node in result)
    node_db.collection.find.assert_called_once_with()

def test_get_all_nodes_failure(node_db):
    """Test failure when retrieving all nodes"""
    node_db.collection.find.side_effect = PyMongoError("DB error")
    
    with pytest.raises(RuntimeError, match="Database operation failed"):
        node_db.get_all_nodes()

def test_update_node_success(node_db):
    """Test successful node update"""
    existing_node = {**SAMPLE_NODE}
    update_data = {"status": "inactive"}
    
    # Mock the get_node call
    node_db.get_node = MagicMock(return_value=Node(**existing_node))
    
    # Mock the update result
    mock_result = MagicMock()
    mock_result.modified_count = 1
    node_db.collection.update_one.return_value = mock_result
    
    result = node_db.update_node("test_node_1", update_data)
    assert isinstance(result, Node)
    assert result.status == "inactive"
    node_db.collection.update_one.assert_called_once()

def test_update_node_not_found(node_db):
    """Test update of non-existent node"""
    node_db.get_node = MagicMock(return_value=None)
    
    result = node_db.update_node("nonexistent_node", {"status": "inactive"})
    assert result is None

def test_update_node_failure(node_db):
    """Test node update failure"""
    node_db.get_node = MagicMock(return_value=Node(**SAMPLE_NODE))
    node_db.collection.update_one.side_effect = PyMongoError("DB error")
    
    with pytest.raises(RuntimeError, match="Updating dabatase failed"):
        node_db.update_node("test_node_1", {"status": "inactive"})

def test_delete_node_success(node_db):
    """Test successful node deletion"""
    mock_result = MagicMock()
    mock_result.deleted_count = 1
    node_db.collection.delete_one.return_value = mock_result
    
    result = node_db.delete_node("test_node_1")
    assert result is True
    node_db.collection.delete_one.assert_called_once_with({"node_id": "test_node_1"})

def test_delete_node_not_found(node_db):
    """Test deletion of non-existent node"""
    mock_result = MagicMock()
    mock_result.deleted_count = 0
    node_db.collection.delete_one.return_value = mock_result
    
    result = node_db.delete_node("nonexistent_node")
    assert result is False

def test_delete_node_failure(node_db):
    """Test node deletion failure"""
    node_db.collection.delete_one.side_effect = PyMongoError("DB error")
    
    with pytest.raises(RuntimeError, match="Deleting database failed"):
        node_db.delete_node("test_node_1")

def test_node_exists_true(node_db):
    """Test node existence check (exists)"""
    node_db.collection.count_documents.return_value = 1
    
    result = node_db.node_exists("test_node_1")
    assert result is True
    node_db.collection.count_documents.assert_called_once_with({"node_id": "test_node_1"}, limit=1)

def test_node_exists_false(node_db):
    """Test node existence check (doesn't exist)"""
    node_db.collection.count_documents.return_value = 0
    
    result = node_db.node_exists("nonexistent_node")
    assert result is False

def test_node_exists_failure(node_db):
    """Test node existence check failure"""
    node_db.collection.count_documents.side_effect = PyMongoError("DB error")
    
    with pytest.raises(RuntimeError, match="Validation error"):
        node_db.node_exists("test_node_1")

def test_count_nodes_success(node_db):
    """Test successful node count"""
    node_db.collection.estimated_document_count.return_value = 5
    
    result = node_db.count_nodes()
    assert result == 5
    node_db.collection.estimated_document_count.assert_called_once_with()

def test_count_nodes_failure(node_db):
    """Test node count failure"""
    node_db.collection.estimated_document_count.side_effect = PyMongoError("DB error")
    
    with pytest.raises(RuntimeError, match="Failed Operation"):
        node_db.count_nodes()

def test_close(node_db):
    """Test database connection closure"""
    node_db.close()
    node_db.client.close.assert_called_once_with()