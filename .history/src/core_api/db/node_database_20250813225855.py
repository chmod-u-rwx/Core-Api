from typing import List, Optional
from uuid import uuid4
from pymongo.collection import Collection
from models.node import Node

class NodeDatabase:
    """CRUD operations for Node model."""

    def __init__(self, collection: Collection):
        """
        Initialize NodeDatabase with a MongoDB collection (or any object with same API).
        """
        self.collection = collection

    # --- CREATE ---
    def create_node(self, node_data: dict) -> Node:
        """
        Insert a new Node into the DB.
        """
        # Generate an ID if not provided
        if "node_id" not in node_data or not node_data["node_id"]:
            node_data["node_id"] = f"node_{uuid4().hex[:8]}"
        
        node = Node(**node_data)
        self.collection.insert_one(node.dict())
        return node

    # --- READ ---
    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a single Node by node_id.
        """
        data = self.collection.find_one({"node_id": node_id})
        return Node(**data) if data else None

    def list_nodes(self) -> List[Node]:
        """
        Get all Nodes from the DB.
        """
        return [Node(**doc) for doc in self.collection.find()]

    # --- UPDATE ---
    def update_node(self, node_id: str, update_data: dict) -> Optional[Node]:
        """
        Update a Node's data. Allows partial updates.
        """
        # Validate against current Node schema (future-proof)
        existing_node = self.get_node(node_id)
        if not existing_node:
            return None
        
        updated_node_data = existing_node.dict()
        updated_node_data.update(update_data)
        updated_node = Node(**updated_node_data)
        
        self.collection.update_one({"node_id": node_id}, {"$set": updated_node.dict()})
        return updated_node

    # --- DELETE ---
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a Node by node_id.
        """
        result = self.collection.delete_one({"node_id": node_id})
        return result.deleted_count > 0
