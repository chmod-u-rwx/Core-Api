import pytest
from mongomock import MongoClient
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any

# --- Define your Node model if not already imported ---
class Node(BaseModel):
    node_id: str = Field(..., min_length=1)
    job_slots: int = Field(..., ge=0)

# --- Test Implementation ---
@pytest.fixture
def mock_db():
    """Fixture that provides a mock MongoDB client"""
    client = MongoClient()
    db = client.get_database("test_db")
    collection = db["nodes"]
    collection.create_index("node_id", unique=True)  # Create unique index
    return collection

@pytest.fixture
def node_db(mock_db):
    """Fixture that provides a test NodeDatabase instance"""
    class TestNodeDatabase:
        def __init__(self):
            self.collection = mock_db

        def create_node(self, node_data: Dict[str, Any]) -> Node:
            try:
                node = Node(**node_data)
                result = self.collection.insert_one(node.model_dump())
                if not result.acknowledged:
                    raise RuntimeError("Failed to create node")
                return node
            except DuplicateKeyError:
                raise ValueError(f"Node with ID {node_data.get('node_id')} already exists")

        def get_node(self, node_id: str) -> Optional[Node]:
            data = self.collection.find_one({"node_id": node_id})
            return Node(**data) if data else None

        # Add other methods following the same pattern...
        
    return TestNodeDatabase()

# --- Test Cases ---
def test_create_and_get_node(node_db):
    """Test creating and retrieving a node"""
    # Create
    node = node_db.create_node({"node_id": "node1", "job_slots": 4})
    assert isinstance(node, Node)
    assert node.node_id == "node1"
    assert node.job_slots == 4
    
    # Retrieve
    fetched = node_db.get_node("node1")
    assert fetched == node

def test_duplicate_node(node_db):
    """Test duplicate node prevention"""
    node_db.create_node({"node_id": "node1", "job_slots": 2})
    with pytest.raises(ValueError, match="already exists"):
        node_db.create_node({"node_id": "node1", "job_slots": 4})

def test_get_nonexistent_node(node_db):
    """Test getting a non-existent node"""
    assert node_db.get_node("nonexistent") is None

def test_invalid_node_data(node_db):
    """Test validation of node data"""
    with pytest.raises(ValueError):
        # Negative job_slots should fail
        node_db.create_node({"node_id": "bad_node", "job_slots": -1})