import pytest
from unittest.mock import patch, MagicMock
from pymongo.errors import PyMongoError, DuplicateKeyError
from models.node import Node
from db.node_database import NodeDatabase

@pytest.fixture
def mock_db():
    with patch('pymongo.MongoClient') as mock_client:
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        yield mock_collection

def test_insert_node_success(mock_db):
    mock_result = MagicMock()
    mock_result.acknowledged = True
    mock_db.insert_one.return_value = mock_result
    
    db = NodeDatabase()
    node_data = {"node_id": "node1", "job_slots": 4}
    result = db.insert_node(node_data)
    
    assert isinstance(result, Node)
    assert result.node_id == "node1"
    assert result.job_slots == 4
    mock_db.insert_one.assert_called_once()

def test_insert_node_duplicate(mock_db):
    mock_db.insert_one.side_effect = DuplicateKeyError("Duplicate")
    
    db = NodeDatabase()
    with pytest.raises(ValueError):
        db.insert_node({"node_id": "node1", "job_slots": 4})

def test_get_node(mock_db):
    mock_data = {"node_id": "node1", "job_slots": 4}
    mock_db.find_one.return_value = mock_data
    
    db = NodeDatabase()
    result = db.get_node("node1")
    
    assert isinstance(result, Node)
    assert result.node_id == "node1"
    mock_db.find_one.assert_called_once_with({"node_id": "node1"})

def test_get_all_nodes(mock_db):
    mock_data = [
        {"node_id": "node1", "job_slots": 4},
        {"node_id": "node2", "job_slots": 8}
    ]
    mock_db.find.return_value = mock_data
    
    db = NodeDatabase()
    results = db.get_all_nodes()
    
    assert len(results) == 2
    assert all(isinstance(node, Node) for node in results)
    mock_db.find.assert_called_once_with()

def test_update_node(mock_db):
    mock_data = {"node_id": "node1", "job_slots": 8}
    mock_db.find_one_and_update.return_value = mock_data
    
    db = NodeDatabase()
    result = db.update_node("node1", {"job_slots": 8})
    
    assert isinstance(result, Node)
    assert result.job_slots == 8
    mock_db.find_one_and_update.assert_called_once_with(
        {"node_id": "node1"},
        {"$set": {"job_slots": 8}},
        return_document=ReturnDocument.AFTER
    )

def test_delete_node(mock_db):
    mock_result = MagicMock()
    mock_result.deleted_count = 1
    mock_db.delete_one.return_value = mock_result
    
    db = NodeDatabase()
    result = db.delete_node("node1")
    
    assert result is True
    mock_db.delete_one.assert_called_once_with({"node_id": "node1"})

def test_count_nodes(mock_db):
    mock_db.count_documents.return_value = 5
    
    db = NodeDatabase()
    result = db.count_nodes()
    
    assert result == 5
    mock_db.count_documents.assert_called_once_with({})