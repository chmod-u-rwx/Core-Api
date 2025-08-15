from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from ..db.connection import get_mongo_client
from ..config import DATABASE_CONNECT_TIMEOUT, DATABASE_URL 


class NodeDataBase:
    # initialize the existing db connection.py
    def __init__(self, db_name: str = "node_database"):
                 
        self.client = get_mongo_client()
        self.db = self.client[db_name]
        self.nodes: Collection = self.db.nodes
        self._initialize_collection()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _initialize_collection(self):
        try: #create index on node_id for uniqueness and fast lookups
            self.nodes.create_index([("id, 1")], unique=True, background=True)
            self.logger.info("Node collection initialized with unique index on node_id.")
        except DuplicateKeyError:
            self.logger.warning("Node collection already exists with unique index on node_id.")
        except PyMongoError as m:
            self.logger.error(f"Failed to initialize node collection: {a}")
            raise RuntimeError(f"Error with the database: {a}")