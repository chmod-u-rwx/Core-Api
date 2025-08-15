from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from ..db.connection import get_mongo_client
from ..config import DATABASE_CONNECT_TIMEOUT, DATABASE_URL 


class NodeDataBase:
    def __init__(self, db_name: str = "test_db""):
        self.client = get_mongo_client()
        self.db = self.client[db_name]
        self.collection: Collection = self.db[collection_name]
        self.collection.create_index("job_slots", unique=True)