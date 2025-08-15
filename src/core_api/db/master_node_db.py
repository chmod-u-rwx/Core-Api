from typing import Any
from pymongo import ASCENDING
from pymongo.database import Database
from pymongo.collection import Collection 
from src.core_api.config import DATABASE_NAME
from src.core_api.db.connection import get_mongo_client

class MasterNodeDatabase:
    def __init__(self) -> None:
        self.client = get_mongo_client()
        self.db: Database[Any] = self.client[DATABASE_NAME]
        self.collection: Collection[Any] = self.collection["master_node"]
        self._create_indexes()
        
    def _create_indexes(self) -> None:
        self.collection.create_index([("master_id", ASCENDING)], name="idx_master_id")