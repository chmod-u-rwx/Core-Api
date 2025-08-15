# src/core_api/db/node_database.py

from typing import List, Optional
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from ..models.node import Node
from .mongo_client import get_mongo_client  # adjust import if filename differs


class NodeDatabase:
    def __init__(self):
        client = get_mongo_client()
        self.db = client.get_database()  # uses default DB from DATABASE_URL
        self.collection: Collection = self.db["nodes"]

    def create_node(self, node_data: dict) -> str:
        """Insert a new node into the database."""
        node = Node(**node_data)
        try:
            result = self.collection.insert_one(node.dict())
            return str(result.inserted_id)
        except PyMongoError as e:
            raise RuntimeError(f"Error creating node: {e}")

    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node by its node_id."""
        try:
            data = self.collection.find_one({"node_id": node_id}, {"_id": 0})
            return Node(**data) if data else None
        except PyMongoError as e:
            raise RuntimeError(f"Error retrieving node: {e}")

    def update_node(self, node_id: str, updates: dict) -> bool:
        """Update a node with new data."""
        try:
            # Validate updates against Node model (partial update allowed)
            updated_data = {k: v for k, v in updates.items() if k in Node.__fields__}
            result = self.collection.update_one(
                {"node_id": node_id},
                {"$set": updated_data}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            raise RuntimeError(f"Error updating node: {e}")

    def delete_node(self, node_id: str) -> bool:
        """Delete a node by its node_id."""
        try:
            result = self.collection.delete_one({"node_id": node_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RuntimeError(f"Error deleting node: {e}")

    def list_nodes(self) -> List[Node]:
        """List all nodes."""
        try:
            data = self.collection.find({}, {"_id": 0})
            return [Node(**doc) for doc in data]
        except PyMongoError as e:
            raise RuntimeError(f"Error listing nodes: {e}")
