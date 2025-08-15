# /db/node_database.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.models.node import Node, NodeInDB
import os


class NodeDatabase:
    def __init__(self):
        MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        DB_NAME = os.getenv("DB_NAME", "golem_project")
        COLLECTION_NAME = "nodes"

        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]

    @staticmethod
    def _serialize(doc: dict) -> dict:
        """Convert Mongo _id to string."""
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return doc

    # CREATE
    async def create_node(self, node: Node) -> NodeInDB:
        node_dict = node.dict(by_alias=True)
        result = await self.collection.insert_one(node_dict)
        node_dict["_id"] = str(result.inserted_id)
        return NodeInDB(**node_dict)

    # READ (single)
    async def get_node(self, node_id: str) -> NodeInDB | None:
        doc = await self.collection.find_one({"_id": ObjectId(node_id)})
        if doc:
            return NodeInDB(**self._serialize(doc))
        return None

    # READ (all)
    async def get_all_nodes(self) -> list[NodeInDB]:
        nodes = []
        async for doc in self.collection.find():
            nodes.append(NodeInDB(**self._serialize(doc)))
        return nodes

    # UPDATE
    async def update_node(self, node_id: str, updates: dict) -> bool:
        """
        Updates only provided fields in the Node document.
        Supports adding new fields if model changes in the future.
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(node_id)},
            {"$set": updates}
        )
        return result.modified_count > 0

    # DELETE
    async def delete_node(self, node_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(node_id)})
        return result.deleted_count > 0
