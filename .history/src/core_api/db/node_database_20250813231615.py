from typing import Optional, List
from models.node import Node
from db. connection import get_mongo_client
from pymongo import MongoClient
from pymongo.database import Database

class NodeDatabase:
    def __init__(self):
        self.db = get_mongo_client().get_db()
        self.collection = self.db["nodes"]

    # CREATE
    def create_node(self, node_data: dict) -> Node:
        """Create and store a new node"""
        node = Node(**node_data)
        result = self.collection.insert_one(node.dict())
        if not result.acknowledged:
            raise Exception("Failed to create node")
        return node

    # READ
    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node by ID"""
        data = self.collection.find_one({"node_id": node_id})
        return Node(**data) if data else None

    def get_all_nodes(self) -> List[Node]:
        """Retrieve all nodes"""
        return [Node(**data) for data in self.collection.find()]

    # UPDATE
    def update_node(self, node_id: str, update_data: dict) -> Optional[Node]:
        """Update node attributes"""
        existing = self.get_node(node_id)
        if not existing:
            return None
            
        updated_data = {**existing.dict(), **update_data}
        result = self.collection.update_one(
            {"node_id": node_id},
            {"$set": updated_data}
        )
        
        return self.get_node(node_id) if result.modified_count else None

    # DELETE
    def delete_node(self, node_id: str) -> bool:
        """Remove a node by ID"""
        result = self.collection.delete_one({"node_id": node_id})
        return result.deleted_count > 0

    # UTILITY METHODS (unchanged)
    def node_exists(self, node_id: str) -> bool:
        return self.get_node(node_id) is not None

    def count_nodes(self) -> int:
        return self.collection.count_documents({})