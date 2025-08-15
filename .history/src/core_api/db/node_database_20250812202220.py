from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from ..models.node import Node
from ..db.connection import get_mongo_client

class NodeDatabase:
    def __init__(self, db_name: str = "node_db"):
 
        self.client = get_mongo_client()
        self.db = self.client[db_name]
        self.nodes: Collection = self.db.nodes
        self._initialize_collection()
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _initialize_collection(self) -> None:
        try:
            self.nodes.create_index(
                [("job_slots", 1), ("_last_updated", -1)],
                background=True
            )
            self.logger.info("Database indexes initialized")
        except PyMongoError as e:
            self.logger.error(f"Index creation failed: {e}")
            raise RuntimeError(f"Database initialization error: {e}")

    def create(self, node: Node) -> bool:
        try:
            node_dict = self._node_to_dict(node)
            node_dict["_created"] = datetime.utcnow()
            node_dict["_last_updated"] = datetime.utcnow()
            
            result = self.nodes.insert_one(node_dict)
            return result.acknowledged
            
        except DuplicateKeyError:
            self.logger.warning(f"Duplicate node ID: {node.id}")
            return False
        except PyMongoError as e:
            self.logger.error(f"Create failed: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    def read(self, node_id: str) -> Optional[Node]:
        try:
            if data := self.nodes.find_one({"id": node_id}):
                return self._dict_to_node(data)
            return None
        except PyMongoError as e:
            self.logger.error(f"Read failed for {node_id}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    def read_all(self, 
                filter: Optional[Dict] = None,
                min_slots: Optional[int] = None) -> List[Node]:
        try:
            query = filter or {}
            if min_slots is not None:
                query["job_slots"] = {"$gte": min_slots}
                
            return [
                self._dict_to_node(d) 
                for d in self.nodes.find(query)
            ]
        except PyMongoError as e:
            self.logger.error(f"Read_all failed: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    def update(self, node_id: str, update_data: Dict[str, Any]) -> bool:
        try:
            if existing := self.read(node_id):
                temp_node = existing.copy(update=update_data)
                update_data = self._node_to_dict(temp_node)
                
                result = self.nodes.update_one(
                    {"id": node_id},
                    {
                        "$set": {
                            **update_data,
                            "_last_updated": datetime.utcnow()
                        }
                    }
                )
                return result.modified_count > 0
            return False
        except PyMongoError as e:
            self.logger.error(f"Update failed for {node_id}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    def delete(self, node_id: str) -> bool:
        """Remove a Node by ID."""
        try:
            result = self.nodes.delete_one({"id": node_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            self.logger.error(f"Delete failed for {node_id}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")

    def _node_to_dict(self, node: Node) -> Dict[str, Any]:
        """Convert Node to database-friendly dict."""
        data = node.model_dump()
        # Convert special fields if needed
        return {k: v for k, v in data.items() if v is not None}

    def _dict_to_node(self, data: Dict[str, Any]) -> Node:
        """Convert database dict to Node instance."""
        clean_data = {
            k: v for k, v in data.items() 
            if not k.startswith('_')
        }
        return Node(**clean_data)

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()