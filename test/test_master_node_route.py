from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
import mongomock
from typing import Any
from mongomock import MongoClient

from src.core_api.app import app

@pytest.fixture
def client():
    with patch("src.core_api.db.master_node_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        yield TestClient(app)
        
