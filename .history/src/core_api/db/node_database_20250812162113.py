from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from ..config import DATABASE_CONNECT_TIMEOUT, DATABASE_URL 
from ..db.connection import get_mongo_client
from ..models.node import Node


class NodeDatabase:  # Fixed class name (camelCase to PascalCase)
    def __init__(self, db_name: str = "node_database"):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.client = get_mongo_client()
        self.db = self.client[db_name]
        self.nodes: Collection = self.db.nodes
        self._initialize_collection()

    def _initialize_collection(self):
        try:
            # Create index on id for uniqueness and fast lookups
            self.nodes.create_index([("id", 1)], unique=True, background=True)
            self.logger.info("Indexes initialized successfully")
        except DuplicateKeyError:
            self.logger.warning("Index already exists")
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to create index: {pymongo_error}")
            raise RuntimeError(f"Database initialization failed: {pymongo_error}")
        
    def create(self, node: 'Node') -> bool:
        try:
            node_dict = self._node_to_dict(node)
            node_dict['created_at'] = datetime.utcnow()
            node_dict['updated_at'] = datetime.utcnow()

            result = self.nodes.insert_one(node_dict)
            return result.acknowledged
        except DuplicateKeyError:
            self.logger.warning(f"Node with ID {node.id} already exists")  # Changed to warning
            return False
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to create node {node.id}: {pymongo_error}")
            raise RuntimeError(f"Failed to create node: {pymongo_error}")
        
    def read(self, node_id: str) -> Optional['Node']:
        try:
            node_data = self.nodes.find_one({"id": node_id})
            return self._dict_to_node(node_data) if node_data else None
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to read node {node_id}: {pymongo_error}")
            raise RuntimeError(f"Failed to read node: {pymongo_error}")
        
    def read_all(self, filter: Optional[Dict] = None, 
                projection: Optional[Dict] = None,
                limit: int = 0) -> List['Node']:
        try:  
            filter = filter or {}
            cursor = self.nodes.find(filter, projection).limit(limit)
            return [self._dict_to_node(node_data) for node_data in cursor]
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to read nodes with filter {filter}: {pymongo_error}")
            raise RuntimeError(f"Failed to read nodes: {pymongo_error}")

    def update(self, node: 'Node', partial: bool = False) -> bool:
        try:
            update_data = {"$set": {"updated_at": datetime.utcnow()}}

            node_dict = self._node_to_dict(node)
            if partial:
                for field, value in node_dict.items():
                    if field not in ["id", "created_at"] and value is not None:
                        update_data["$set"][field] = value
            else:
                node_dict['updated_at'] = datetime.utcnow()
                update_data = {"$set": node_dict}
                update_data["$setOnInsert"] = {"created_at": node_dict.get("created_at", datetime.utcnow())}

            result = self.nodes.update_one(
                {"id": node.id},
                update_data,
                upsert=False
            )
            return result.modified_count > 0
        
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to update node {node.id}: {pymongo_error}")
            raise RuntimeError(f"Failed to update node: {pymongo_error}") 
        
    def delete(self, node_id: str) -> bool:
        try:
            result = self.nodes.delete_one({"id": node_id})
            return result.deleted_count > 0
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to delete node {node_id}: {pymongo_error}")
            raise RuntimeError(f"Failed to delete node: {pymongo_error}")
    
    def count(self, filter: Optional[Dict] = None) -> int:
        try:
            filter = filter or {}
            return self.nodes.count_documents(filter)
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to count nodes: {pymongo_error}")
            raise RuntimeError(f"Failed to count nodes: {pymongo_error}")
    
    def _node_to_dict(self, node: 'Node') -> Dict[str, Any]:
        if hasattr(node, 'model_dump'):  # Pydantic v2
            return node.model_dump()
        elif hasattr(node, 'dict'):  # Pydantic v1
            return node.dict()
        elif hasattr(node, '__dict__'):  # Plain Python object
            return vars(node).copy()
        else:
            raise ValueError("Unsupported Node type")

    def _dict_to_node(self, node_data: Dict[str, Any]) -> 'Node':
        if not node_data or 'id' not in node_data:
            raise ValueError("Node data must contain 'id' field")
            
        node_data.pop('_id', None)  # Remove MongoDB internal ID
        
        if hasattr(Node, 'model_validate'):  # Pydantic v2
            return Node.model_validate(node_data)
        elif hasattr(Node, 'parse_obj'):  # Pydantic v1
            return Node.parse_obj(node_data)
        else:
            return Node(**node_data)
        
    def close(self):
        if self.client:
            self.client.close()
            self.logger.info("MongoDB connection closed")
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()