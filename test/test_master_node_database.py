import mongomock
import pytest
from typing import Any
from mongomock import MongoClient
from unittest.mock import patch
from src.core_api.db.master_node_db import MasterNodeDatabase

@pytest.fixture
def master_node_db():
    with patch("src.core_api.db.master_node_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        db = MasterNodeDatabase()
        yield db
        
def test_collection_and_index(master_node_db: MasterNodeDatabase):
    assert master_node_db.collection.name == "master_node"
    
    indexes = master_node_db.collection.index_information()
    assert "idx_master_id" in indexes