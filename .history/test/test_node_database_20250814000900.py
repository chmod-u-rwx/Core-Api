from typing import List, Optional, Dict, Any
from pymongo.collection import Collection
from bson import ObjectId
from datetime import datetime
from src.core_api.mongo_connection import get_mongo_client
from ..models.node import Node

class NodeDatabase:
    def __init__(self):
        self.db_name = "nodes_database"
        self.collection_name = "nodes"

    def _get_collection(self) -> Collection:
        client = get_mongo_client()
        return client[self.db_name][self.collection_name]

    def create_node(self, node_data: Dict[str, Any]) -> str:
        node_data["created_at"] = datetime.utcnow()
        result = self._get_collection().insert_one(node_data)
        return str(result.inserted_id)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        node = self._get_collection().find_one({"_id": ObjectId(node_id)})
        if node:
            node["_id"] = str(node["_id"])
        return node

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        nodes = list(self._get_collection().find())
        for node in nodes:
            node["_id"] = str(node["_id"])
        return nodes

    def update_node(self, node_id: str, update_data: Dict[str, Any]) -> bool:
        result = self._get_collection().update_one(
            {"_id": ObjectId(node_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    def delete_node(self, node_id: str) -> bool:
        result = self._get_collection().delete_one({"_id": ObjectId(node_id)})
        return result.deleted_count > 0
