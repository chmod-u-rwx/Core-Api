from typing import Dict, Optional, List, Any
from uuid import UUID
from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError
from ..models.node_model import Node
from ..config import DATABASE_URL, DATABASE_CONNECT_TIMEOUT, DATABASE_NAME

class NodeDatabase:
    def __init__(self, collection= "Nodes"):
        self.client = self.get_mongo_client()
        self.db = self.client[DATABASE_NAME] 
        self.collection = self.db["Nodes"]
        self._check_indexes()

    def get_mongo_client(self) -> MongoClient[Any]:
        try:
            client: MongoClient[Any] = MongoClient(
                DATABASE_URL,
                connectTimeoutMS=DATABASE_CONNECT_TIMEOUT
            )
            client.admin.command('ping')
            return client
        except PyMongoError as e:
            raise RuntimeError(f"MongoDB connection failed: {e}")

    def _check_indexes(self):
        try:
            self.collection.create_index("node_id", unique=True)
        except PyMongoError as e:
            raise RuntimeError(f"Index creation failed: {e}")

    def create_node(self, node_data: Node):
        node = Node(**node_data)
        db_data = node.model_dump()
        db_data["node_id"] = str(db_data["node_id"]) #string conversion
        try:
            self.collection.insert_one(db_data)
            return node
        except DuplicateKeyError:
            raise ValueError(f"Node with ID {node.node_id} already exists")
        except PyMongoError as e:
            raise RuntimeError(f"Creating node failed: {e}")

    def get_node(self, node_id) -> Optional[Node]:
        node_id_str = str(node_id)
        data = self.collection.find_one({"node_id": node_id_str})
        if not data:
            return None
        data["node_id"] = UUID(data["node_id"])
        return Node(**data)

    def get_all_nodes(self) -> List[Node]:
        try:
            nodes = []
            for data in self.collection.find():
                data["node_id"] = UUID(data["node_id"])
                nodes.append(Node(**data))
            return nodes
        except PyMongoError as e:
            raise RuntimeError(f"Fetching all nodes failed: {e}")

    def update_node(self, node_id, update_data:Node):
        node_id_str = str(node_id)
        existing = self.get_node(node_id)
        if not existing:
            return None
        updated_data = {**existing.model_dump(), **update_data}
        updated_data["node_id"] = str(updated_data["node_id"])
        self.collection.update_one({"node_id": node_id_str}, {"$set": updated_data})
        updated_data["node_id"] = UUID(updated_data["node_id"])
        return Node(**updated_data)

    def delete_node(self, node_id) -> bool:
        node_id_str = str(node_id)
        result = self.collection.delete_one({"node_id": node_id_str})
        return result.deleted_count > 0

    def count_nodes(self) -> int:
        try:
            return self.collection.estimated_document_count()
        except PyMongoError as e:
            raise RuntimeError(f"Counting nodes failed: {e}")

    def close(self):
        if hasattr(self, "client"):
            self.client.close()
