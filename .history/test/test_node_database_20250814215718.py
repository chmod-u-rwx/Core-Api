import pytest
from unittest.mock import patch, MagicMock
from pymongo.errors import DuplicateKeyError
from src.core_api.models.node import Node
from src.core_api.db.node_database import NodeDatabase

@pytest.fixture
def mock_collection():
    with patch("pymongo.MongoClient") as mock_client:
        mock_client_instance = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        # Simulate db.get_database() returning mock_db
        mock_client_instance.get_database.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        mock_client.return_value = mock_client_instance
        yield mock_collection


def test_create_node_success(mock_collection):
    mock_result = MagicMock()
    mock_result.acknowledged = True
    mock_collection.insert_one.return_value = mock_result

    db = NodeDatabase()
    node_data = {"node_id": "node1", "name": "Test Node"}
    result = db.create_node(node_data)

    assert isinstance(result, Node)
    assert result.node_id == "node1"
    mock_collection.insert_one.assert_called_once()


def test_create_node_duplicate(mock_collection):
    mock_collection.insert_one.side_effect = DuplicateKeyError("Duplicate")

    db = NodeDatabase()
    with pytest.raises(ValueError):
        db.create_node({"node_id": "node1", "name": "Test Node"})


def test_get_node_found(mock_collection):
    mock_collection.find_one.return_value = {"node_id": "node1", "name": "Test Node"}

    db = NodeDatabase()
    node = db.get_node("node1")

    assert isinstance(node, Node)
    assert node.node_id == "node1"
    mock_collection.find_one.assert_called_once_with({"node_id": "node1"})


def test_get_node_not_found(mock_collection):
    mock_collection.find_one.return_value = None

    db = NodeDatabase()
    node = db.get_node("nodeX")

    assert node is None
    mock_collection.find_one.assert_called_once_with({"node_id": "nodeX"})


def test_get_all_nodes(mock_collection):
    mock_collection.find.return_value = [
        {"node_id": "node1", "name": "Node1"},
        {"node_id": "node2", "name": "Node2"}
    ]

    db = NodeDatabase()
    nodes = db.get_all_nodes()

    assert len(nodes) == 2
    assert all(isinstance(n, Node) for n in nodes)
    mock_collection.find.assert_called_once()


def test_update_node_success(mock_collection):
    # Simulate existing node
    mock_collection.find_one.return_value = {"node_id": "node1", "name": "Old Name"}

    mock_result = MagicMock()
    mock_result.modified_count = 1
    mock_collection.update_one.return_value = mock_result

    db = NodeDatabase()
    updated_node = db.update_node("node1", {"name": "New Name"})

    assert isinstance(updated_node, Node)
    assert updated_node.name == "New Name"
    mock_collection.update_one.assert_called_once()


def test_update_node_not_found(mock_collection):
    mock_collection.find_one.return_value = None

    db = NodeDatabase()
    updated_node = db.update_node("nodeX", {"name": "New Name"})

    assert updated_node is None


def test_delete_node_success(mock_collection):
    mock_result = MagicMock()
    mock_result.deleted_count = 1
    mock_collection.delete_one.return_value = mock_result

    db = NodeDatabase()
    deleted = db.delete_node("node1")

    assert deleted is True
    mock_collection.delete_one.assert_called_once_with({"node_id": "node1"})


def test_delete_node_not_found(mock_collection):
    mock_result = MagicMock()
    mock_result.deleted_count = 0
    mock_collection.delete_one.return_value = mock_result

    db = NodeDatabase()
    deleted = db.delete_node("nodeX")

    assert deleted is False


def test_count_nodes(mock_collection):
    mock_collection.estimated_document_count.return_value = 5

    db = NodeDatabase()
    count = db.count_nodes()

    assert count == 5
    mock_collection.estimated_document_count.assert_called_once()
