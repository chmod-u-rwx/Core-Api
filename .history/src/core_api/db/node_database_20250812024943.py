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
            self.logger.info("Successful")
        except DuplicateKeyError:
            self.logger.warning("Existing index")
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to create index: {pymongo_error}")
            raise RuntimeError(f"Error with the database initialization: {pymongo_error}")
        
    def create(self, node: 'Node') -> bool:
        try:
            node_dict = self._node_to_dict(node)
            node_dict['created_at'] = datetime.utcnow()
            node_dict['updated_at'] = datetime.utcnow()

            result = self.nodes.insert_one(node_dict)
            return result.acknowledged
        except DuplicateKeyError:
            self.logger.error(f"Node with this ID {node.id} already exists.")
            return False
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to create node: {node.id} {pymongo_error}")
            raise RuntimeError(f"Error creating node: {pymongo_error}")
        
    def read(self, node_id: str) -> Optional['Node']:
        try:
            node_data = self.nodes.find_one({"id": node_id})
            if node_data:
                return self._dict_to_node(node_data)
            return None
        
        except PyMongoError as pymongo_error:

        
