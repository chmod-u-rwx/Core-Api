from mongo_config import MongoConfig
from mongo_helper import MongoDBHelper

def setup_database():
    config = MongoConfig.from_env(
        database_name="test_db",
        connect_timeout_ms=5000,
    )

    MongoDBHelper.initialize(config)