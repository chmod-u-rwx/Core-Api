import pytest
from pytest import MonkeyPatch
from mongomock import MongoClient
from core_api.db.mongo_helper import MongoDBHelper
from core_api.db.mongo_config import MongoConfig
from test_mongo_config import mock_mongo_config

@pytest.fixture
def mongodb_helper(mock_mongo_config: MongoConfig, monkeypatch: MonkeyPatch):
    monkeypatch.setattr("core_api.db.mongo_helper.MongoClient", MongoClient)
    
    MongoDBHelper.initialize(mock_mongo_config)
    yield
    MongoDBHelper.close()
    
def test_mongodb_connection(mongodb_helper: MongoDBHelper):
    db = MongoDBHelper.get_db()
    assert db.command('ping')['ok'] == 1.0
    
def test_db_operations(mongodb_helper: MongoDBHelper):
    db = MongoDBHelper.get_db()
    collection = db["test_collection"]
    
    test_data: dict[str, int | str] = {"name": "test", "value": 123}
    inserted_id = collection.insert_one(test_data).inserted_id
    retrieved = collection.find_one({"_id": inserted_id})
    
    assert retrieved is not None, "No document found"
    assert retrieved["name"] == "test"
    assert retrieved["value"] == 123