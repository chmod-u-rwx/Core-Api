from typing import Dict, Optional, List, Any
from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError
from models.node import Node
from ..config import DATABASE_URL, DATABASE_CONNECT_TIMEOUT

class NodeDatabase:
    def __init__(self):
        self.client = self._get_client()
        self.db = self.client.get_database()
        self.collection = self.db["nodes"]
        self._ensure_indexes()

    def _get_client(self) -> MongoClient[Any]:
        """Get MongoDB client with error handling"""
        try:
            client: MongoClient[Any] = MongoClient(
                DATABASE_URL,
                connectTimeoutMS=DATABASE_CONNECT_TIMEOUT
            )
            client.admin.command('ping')
            return client
        except PyMongoError as e:
            raise RuntimeError(f"MongoDB connection failed: {e}")

    def _ensure_indexes(self):
        """Create necessary indexes"""
        try:
            self.collection.create_index("node_id", unique=True)
        except PyMongoError as e:
            raise RuntimeError(f"Index creation failed: {e}")

    # CREATE
    def create_node(self, node_data: Dict[str, Any]) -> Node:
        """Create and store a new node"""
        try:
            node = Node(**node_data)
            result = self.collection.insert_one(node.model())
            if not result.acknowledged:
                raise RuntimeError("Failed to create node")
            return node
        except DuplicateKeyError:
            raise ValueError(f"Node with ID {node_data.get('node_id')} already exists")
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {e}")

    # READ
    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node by ID"""
        try:
            data = self.collection.find_one({"node_id": node_id})
            return Node(**data) if data else None
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {e}")

    def get_all_nodes(self) -> List[Node]:
        """Retrieve all nodes"""
        try:
            return [Node(**data) for data in self.collection.find()]
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {e}")

    # UPDATE
    def update_node(self, node_id: str, update_data: Dict[str, Any]) -> Optional[Node]:
        """Update node attributes"""
        try:
            existing = self.get_node(node_id)
            if not existing:
                return None

            # Merge existing data with updates
            updated_data = {**existing.dict(), **update_data}
            result = self.collection.update_one(
                {"node_id": node_id},
                {"$set": updated_data}
            )
            
            if result.modified_count == 0:
                return None
            return Node(**updated_data)
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {e}")

    # DELETE
    def delete_node(self, node_id: str) -> bool:
        """Remove a node by ID"""
        try:
            result = self.collection.delete_one({"node_id": node_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {e}")

    # UTILITY METHODS
    def node_exists(self, node_id: str) -> bool:
        """Check if a node exists"""
        try:
            return self.collection.count_documents({"node_id": node_id}, limit=1) > 0
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {e}")

    def count_nodes(self) -> int:
        """Get total number of nodes"""
        try:
            return self.collection.estimated_document_count()
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {e}")

    def close(self):
        """Close the database connection"""
        self.client.close()