from typing import Optional, List, Dict
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError, DuplicateKeyError
from models.node import Node

class NodeDatabase:
    def __init__(self, connection_string: str = "mongodb://localhost:27017", db_name: str = "node_db"):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db["nodes"]
        self._create_indexes()

    def _create_indexes(self):
        try:
            self.collection.create_index("node_id", unique=True)
        except PyMongoError as e:
            raise RuntimeError(f"Failed to create indexes: {str(e)}")

    def insert_node(self, node_data: Dict) -> Node:
        try:
            node = Node(**node_data)
            result = self.collection.insert_one(node.dict())
            if not result.acknowledged:
                raise RuntimeError("Insert operation not acknowledged")
            return node
        except DuplicateKeyError:
            raise ValueError(f"Node with ID {node_data.get('node_id')} already exists")
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {str(e)}")

    def get_node(self, node_id: str) -> Optional[Node]:
        try:
            data = self.collection.find_one({"node_id": node_id})
            return Node(**data) if data else None
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {str(e)}")

    def get_all_nodes(self) -> List[Node]:
        try:
            return [Node(**data) for data in self.collection.find()]
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {str(e)}")

    def update_node(self, node_id: str, update_data: Dict) -> Optional[Node]:
        try:
            result = self.collection.find_one_and_update(
                {"node_id": node_id},
                {"$set": update_data},
                return_document=ReturnDocument.AFTER
            )
            return Node(**result) if result else None
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {str(e)}")

    def delete_node(self, node_id: str) -> bool:
        try:
            result = self.collection.delete_one({"node_id": node_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {str(e)}")

    def count_nodes(self) -> int:
        try:
            return self.collection.count_documents({})
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed: {str(e)}")

    def close(self):
        self.client.close()