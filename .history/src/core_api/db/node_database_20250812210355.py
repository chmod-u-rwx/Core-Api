# node_database.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.models.node import Node, NodeInDB
from typing import Optional, List
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "golem_project")
COLLECTION_NAME = "nodes"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Helper: Convert MongoDB doc to NodeInDB
def serialize_node(doc) -> NodeInDB:
    doc["_id"] = str(doc["_id"])
    return NodeInDB(**doc)

# Create Node
async def create_node(node: Node) -> NodeInDB:
    node_dict = node.model_dump()  # works with Pydantic v2
    result = await collection.insert_one(node_dict)
    node_dict["_id"] = str(result.inserted_id)
    return NodeInDB(**node_dict)

# Get Node by ID
async def get_node(node_id: str) -> Optional[NodeInDB]:
    try:
        doc = await collection.find_one({"_id": ObjectId(node_id)})
    except Exception:
        return None
    return serialize_node(doc) if doc else None

# Get All Nodes
async def get_all_nodes() -> List[NodeInDB]:
    nodes = []
    async for doc in collection.find():
        nodes.append(serialize_node(doc))
    return nodes

# Update Node
async def update_node(node_id: str, updates: dict) -> bool:
    if "_id" in updates:  # Don't allow updating _id
        updates.pop("_id")
    try:
        result = await collection.update_one(
            {"_id": ObjectId(node_id)},
            {"$set": updates}
        )
        return result.modified_count > 0
    except Exception:
        return False

# Delete Node
async def delete_node(node_id: str) -> bool:
    try:
        result = await collection.delete_one({"_id": ObjectId(node_id)})
        return result.deleted_count > 0
    except Exception:
        return False
