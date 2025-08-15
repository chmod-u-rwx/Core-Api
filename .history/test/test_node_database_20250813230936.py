import pytest
from uuid import uuid4
from pymongo import MongoClient
from core_api.db.node_database import NodeDatabase
from core_api.models.node import Node
from core_api.db.connection import get_mongo_client


@pytest.fixture(scope="module")
def get_mongo_test_db():
    """
    Connect to a dedicated test database and ensure it's empty before/after tests.
    """
    client: MongoClient = get_mongo_client()
    db = client["test_db"]  # change name if you prefer
    db["test_nodes"].delete_many({})  # cleanup before
    yield db
    db["test_nodes"].delete_many({})  # cleanup after


@pytest.fixture
def node_db(mongo_test_db):
    """
    Override NodeDatabase to use the test_nodes collection.
    """
    db_instance = NodeDatabase()
    db_instance.collection = mongo_test_db["test_nodes"]
    return db_instance


def test_create_and_get_node(node_db):
    node_id = str(uuid4())
    node_data = {
        "node_id": node_id,
        "name": "Test Node",
        "description": "A node for unit testing",
        "status": "active"
    }

    # Create
    inserted_id = node_db.create_node(node_data)
    assert inserted_id is not None

    # Get
    retrieved = node_db.get_node(node_id)
    assert retrieved is not None
    assert retrieved.node_id == node_id
    assert retrieved.name == "Test Node"


def test_update_node(node_db):
    node_id = str(uuid4())
    node_db.create_node({
        "node_id": node_id,
        "name": "Old Name",
        "description": "Old Desc",
        "status": "inactive"
    })

    # Update
    updated = node_db.update_node(node_id, {"name": "New Name", "status": "active"})
    assert updated is True

    # Check update
    retrieved = node_db.get_node(node_id)
    assert retrieved.name == "New Name"
    assert retrieved.status == "active"


def test_delete_node(node_db):
    node_id = str(uuid4())
    node_db.create_node({
        "node_id": node_id,
        "name": "Delete Me",
        "description": "Temporary",
        "status": "active"
    })

    deleted = node_db.delete_node(node_id)
    assert deleted is True

    # Ensure it's gone
    retrieved = node_db.get_node(node_id)
    assert retrieved is None


def test_list_nodes(node_db):
    # Ensure list works with multiple entries
    node_db.create_node({
        "node_id": str(uuid4()),
        "name": "Node A",
        "description": "First",
        "status": "active"
    })
    node_db.create_node({
        "node_id": str(uuid4()),
        "name": "Node B",
        "description": "Second",
        "status": "inactive"
    })

    nodes = node_db.list_nodes()
    assert isinstance(nodes, list)
    assert len(nodes) >= 2
    assert all(isinstance(n, Node) for n in nodes)
