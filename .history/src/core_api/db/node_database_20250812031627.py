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
            self.logger.error(f"Failed to read node: {node_id} {pymongo_error}")
            raise RuntimeError(f"Error reading node: {pymongo_error}")
        
    def read_all(self, filter: Optional[Dict]  = None, limit: int = 0) -> List['Node']:
        try:  
            if filter is None:
                filter = {}
            if limit > 0:
                nodes_data = self.nodes.find(filter).limit(limit)
            else:
                nodes_data = self.nodes.find(filter)

            return [self._dict_to_node(node_data) for node_data in nodes_data]
        
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to read all nodes with filter {filter}: {pymongo_error}")
            raise RuntimeError(f"Error reading all nodes with filter {filter}: {pymongo_error}")

    def update(self, node: 'Node', partial: bool = False) -> bool:
        try:
            update_data = {"$set": {"update_at": datetime.utcnow()}}

            if partial:
                node_dict = self._node_to_dict(node)
                for field, value in node_dict.items():
                    if value is not None: # dont update if value is None
                        update_data["$set"][field] = value
            else:
                node_dict = self._node_to_dict(node)
                node_dict['updated_at'] = datetime.utcnow()
                update_data["$set"].update(node_dict)
                update_data["$setOnInsert"] = {"created_at": node_dict.get("created_at", datetime.utcnow())}
                result = self.nodes.update_one({"id": node.id}, update_data, upsert=False) # upsert=False means it will not create a new document if it does not exist  
        
            return result.modified_count > 0 or result.upserted_id is not None # modified or created
        
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to update node: {node.id} {pymongo_error}")
            raise RuntimeError(f"Error updating node: {pymongo_error}") 
        
    def delete(self, node_id: str) -> bool:
        try:
            result = self.nodes.delete_one({"id": node_id})
            return result.deleted_count > 0
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to delete node: {node_id} {pymongo_error}")
            raise RuntimeError(f"Error deleting node: {pymongo_error}")
        

