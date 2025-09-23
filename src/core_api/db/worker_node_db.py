from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pymongo.errors import PyMongoError, DuplicateKeyError
from ..models.worker_node import WorkerNode, WorkerNodeUpdates, WorkerNodeResources
from .connection import get_mongo_client
from ..config import DATABASE_NAME

class InvalidUpdate(Exception):
    ...

class WorkerNodeDatabase:
    def __init__(self):
        self.client = get_mongo_client()
        self.db = self.client[DATABASE_NAME] 
        self.nodes = self.db["Nodes"]
        self._check_indexes()

    def _check_indexes(self):
        try:
            self.nodes.create_index("node_id", unique=True)
        except PyMongoError as e:
            raise RuntimeError(f"Index creation failed: {e}")

    def create_node(self, node_data: WorkerNode) -> WorkerNode:
        db_data = node_data.model_dump()
        db_data["node_id"] = str(db_data["node_id"])
        try:
            self.nodes.insert_one(db_data)
            return node_data
        except DuplicateKeyError:
            raise ValueError(f"Node with ID {node_data.node_id} already exists")
        except PyMongoError as e:
            raise RuntimeError(f"Creating node failed: {e}")

    def get_node(self, node_id: UUID) -> WorkerNode:
        data = self.nodes.find_one({"node_id": str(node_id)})
        if not data:
            raise KeyError(f"Node with ID {node_id} does not exist")
        data["node_id"] = UUID(data["node_id"])
        return WorkerNode(**data)

    def get_all_nodes(self) -> List[WorkerNode]:
        try:
            nodes: List[WorkerNode] = []
            for data in self.nodes.find():
                data["node_id"] = UUID(data["node_id"])
                nodes.append(WorkerNode(**data))
            return nodes
        except PyMongoError as e:
            raise RuntimeError(f"Fetching all nodes failed: {e}")

    def update_node(self, node_id: UUID, update_data: WorkerNodeUpdates) -> WorkerNode:
        node_id_str = str(node_id)
        existing = self.get_node(node_id)  # will raise if not found
        if not existing:
            raise KeyError(f"Node with ID {node_id} does not exist")
        update_fields = update_data.model_dump(exclude_unset=True)

        if not update_fields:
            raise InvalidUpdate("Nothing to update")

        result = self.nodes.update_one(
                                        {"node_id": node_id_str},
                                        {"$set": update_fields})

        if result.modified_count == 0:
            raise RuntimeError("Failed to update. Mongo db did not update anything")

        updated = self.get_node(node_id)
        return updated

    def delete_node(self, node_id: UUID) -> bool:
        result = self.nodes.delete_one({"node_id": str(node_id)})
        return result.deleted_count > 0

    def count_nodes(self) -> int:
        try:
            return self.nodes.estimated_document_count()
        except PyMongoError as e:
            raise RuntimeError(f"Counting nodes failed: {e}")

    def close(self):
        if hasattr(self, "client"):
            self.client.close()

class WorkerNodeResourceDatabase:
    def __init__(self):
        self.client = get_mongo_client()
        self.db = self.client[DATABASE_NAME] 
        self.collection = self.db["NodeResources"]
        self._check_indexes()

    def _check_indexes(self):
        try:
            self.collection.create_index("worker_id")
            self.collection.create_index("timestamp")
        except PyMongoError as e:
            raise RuntimeError(f"Index creation failed: {e}")
        
    def insert(self, resource: WorkerNodeResources) -> WorkerNodeResources:
        db_data = resource.model_dump()
        db_data["worker_id"] = str(db_data["worker_id"])
        try:
            result = self.collection.insert_one(db_data)
            if not result.acknowledged:
                raise RuntimeError("Inserting resource report failed: not acknowledged")
            if not result.inserted_id:
                raise RuntimeError("Inserting resource report failed: no inserted_id")
            return resource
        except PyMongoError as e:
            raise RuntimeError(f"Inserting resource report failed: {e}")
    
    def list_resources(self, 
                       worker_id: Optional[UUID] = None, 
                       start_time: Optional[datetime] = None, 
                       end_time: Optional[datetime] = None) -> List[WorkerNodeResources]:
        try:
            query = {}
            
            if worker_id:
                query["worker_id"] = str(worker_id)
            if start_time or end_time:
                query["timestamp"] = {}
                if start_time:
                    query["timestamp"]["$gte"] = start_time
                if end_time:
                    query["timestamp"]["$lte"] = end_time
                
            docs = list(self.collection.find(query))
            
            return [WorkerNodeResources(**doc) for doc in docs]
        except PyMongoError as e:
            raise RuntimeError(f"Listing resource reports failed: {e}")