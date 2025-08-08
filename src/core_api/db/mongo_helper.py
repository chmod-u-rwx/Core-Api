from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Any, Optional
from core_api.db.mongo_config import MongoConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBHelper:
    _client: Optional[MongoClient[Any]] = None
    _db = None
    
    @classmethod
    def initialize(cls, config: MongoConfig):
        try:
            cls._client = MongoClient(
                config.uri,
                connectTimeoutMs=config.connect_timeout_ms
            )
            cls._db = cls._client[config.database_name]
            
            cls._client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            cls._client = None
            raise
        
    @classmethod
    def get_db(cls):
        if cls._db is None:
            raise RuntimeError("MongoDB connection not initialized")
        return cls._db
    
    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("MongoDB connection closed")