import pytest
from core_api.db.mongo_config import MongoConfig

@pytest.fixture
def mock_mongo_config():
    return MongoConfig(
        uri="mongodb://localhost:27017/",
        database_name="test_db",
        connect_timeout_ms=1000,
    )
    
def test_mock_mongo_config_fixture(mock_mongo_config: MongoConfig):
    assert mock_mongo_config.uri == "mongodb://localhost:27017/"
    assert mock_mongo_config.database_name == "test_db"
    assert mock_mongo_config.connect_timeout_ms == 1000