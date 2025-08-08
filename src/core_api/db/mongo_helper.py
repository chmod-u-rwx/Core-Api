from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Any
from ..config import DATABASE_URL, DATABASE_CONNECT_TIMEOUT

def get_mongo_client():
    try:
        client: MongoClient[Any] = MongoClient(
            DATABASE_URL,
            DATABASE_CONNECT_TIMEOUT,
        )
        
        client.admin.command('ping')        
        return client
        
    except PyMongoError as e:
        raise RuntimeError(f"MongoDB connection failed: {e}")