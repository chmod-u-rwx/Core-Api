# node_database.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.models.node import Node, NodeInDB
import os

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "golem_project")
COLLECTION_NAME = "nodes"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


# Create Node
async def create_node(node: Node) -> NodeInDB:
    node_dict = node.dict()
    result = await collection.insert_one(node_dict)
    node_dict["_id"] = str(result.inserted_id)
    return NodeInDB(**node_dict)


# Get Node by ID
async def get_node(node_id: str) -> NodeInDB | None:
    doc = await collection.find_one({"_id": ObjectId(node_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
        return NodeInDB(**doc)
    return None


# Get All Nodes
async def get_all_nodes() -> list[NodeInDB]:
    nodes = []
    async for doc in collection.find():
        doc["_id"] = str(doc["_id"])
        nodes.append(NodeInDB(**doc))
    return nodes


# Update Node
async def update_node(node_id: str, updates: dict) -> bool:
    result = await collection.update_one(
        {"_id": ObjectId(node_id)},
        {"$set": updates}
    )
    return result.modified_count > 0


# Delete Node
async def delete_node(node_id: str) -> bool:
    result = await collection.delete_one({"_id": ObjectId(node_id)})
    return result.deleted_count > 0
