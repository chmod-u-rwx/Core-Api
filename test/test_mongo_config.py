import pytest
from pytest import MonkeyPatch
from core_api.db.mongo_config import MongoConfig

@pytest.fixture
def mock_mongo_config():
    return MongoConfig(
        uri="mongodb://localhost:27017/",
        database_name="test_db",
        connect_timeout_ms=1000,
    )
    
def test_from_env_with_env(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("MONGODB_URI", "mongodb://custom:27017/")
    config = MongoConfig.from_env(database_name="kissme_db")
    assert config.uri == "mongodb://custom:27017/"
    assert config.database_name == "kissme_db"
    assert config.connect_timeout_ms == 5000
    
def test_from_env_without_env(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("MONGODB_URI", raising=False)
    config = MongoConfig.from_env(database_name="anokaboss_db")
    assert config.uri == "mongodb://localhost:27017/"
    assert config.database_name == "anokaboss_db"
    assert config.connect_timeout_ms == 5000