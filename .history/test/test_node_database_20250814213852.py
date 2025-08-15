# test_node_database.py
import pytest
from uuid import uuid4
from your_module_path.db.node_database import NodeDatabase  # adjust import
from your_module_path.models.node import Node  # adjust import

@pytest.fixture
def node_db():
    """Provide a NodeDatabase instance connected to test DB."""
    db = NodeDatabase()
    # Make sure it's pointing to a test database
    db.db = db.client["test_db"]  # Switch to a test DB
    db.collection = db.db["nodes"]
    db.collection.delete_many({})  # Clean slate before tests
    yield db
    db.collection.delete_many({})
    db.close()

def test_create_and_get_node(node_db):
    node_id = str(uuid4())
    node_data = {
        "node_id": node_id,
        "name": "Test Node",
        "description": "A test node for unit testing"
    }

    # Create node
    created_node = node_db.create_node(node_data)
    assert isinstance(created_node, Node)
    assert created_node.node_id == node_id

    # Get node
    fetched_node = node_db.get_node(node_id)
    assert fetched_node is not None
    assert fetched_node.name == "Test Node"

def test_update_node(node_db):
    node_id = str(uuid4())
    node_data = {
        "node_id": node_id,
        "name": "Old Name",
        "description": "Before update"
    }
    node_db.create_node(node_data)

    updated_node = node_db.update_node(node_id, {"name": "New Name"})
    assert updated_node is not None
    assert updated_node.name == "New Name"

def test_delete_node(node_db):
    node_id = str(uuid4())
    node_data = {
        "node_id": node_id,
        "name": "Delete Me",
        "description": "This will be deleted"
    }
    node_db.create_node(node_data)

    deleted = node_db.delete_node(node_id)
    assert deleted is True
    assert node_db.get_node(node_id) is None

def test_node_exists_and_count(node_db):
    node_id = str(uuid4())
    node_data = {
        "node_id": node_id,
        "name": "Exist Node",
        "description": "Check existence"
    }
    node_db.create_node(node_data)

    assert node_db.node_exists(node_id) is True
    assert node_db.count_nodes() == 1
