import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Any
from ..config import DATABASE_URL, DATABASE_CONNECT_TIMEOUT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_mongo_helper():
    try:
        client: MongoClient[Any] = MongoClient(
            DATABASE_URL,
            DATABASE_CONNECT_TIMEOUT,
        )
        
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        return client
        
    except PyMongoError as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise