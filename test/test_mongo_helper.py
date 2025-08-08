from typing import Any
import pytest
from pytest import MonkeyPatch
from mongomock import MongoClient
from core_api.db.mongo_helper import get_mongo_client

@pytest.fixture
def mock_mongo_client(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("core_api.db.mongo_helper.MongoClient", MongoClient)
    yield
    
def test_mongo_connection(mock_mongo_client: Any):
    client = get_mongo_client()

    assert client is not None
    assert client.admin.command('ping')['ok'] == 1.0
    
def test_mongo_crud(mock_mongo_client: Any):
    client = get_mongo_client()
    db = client["test_db"]
    collection = db["test_collection"]

    test_data: dict[str, int | str] = {"name": "test", "value": 123}
    inserted_id = collection.insert_one(test_data).inserted_id
    retrieved = collection.find_one({"_id": inserted_id})

    assert retrieved is not None
    assert retrieved["name"] == "test"
    assert retrieved["value"] == 123