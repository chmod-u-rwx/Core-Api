from typing import Any, List
from pydantic import UUID4
from pymongo import ASCENDING
from pymongo.errors import PyMongoError
from pymongo.database import Database
from pymongo.collection import Collection 
from src.core_api.models.master_node import MasterNode, UpdateMasterNode
from src.core_api.config import DATABASE_NAME
from src.core_api.db.connection import get_mongo_client

class MasterNodeNotFoundException(Exception):
    ...

class MasterNodeDatabase:
    def __init__(self) -> None:
        try:
            self.client = get_mongo_client()
            self.db: Database[Any] = self.client[DATABASE_NAME]
            self.collection: Collection[Any] = self.db["master_node"]
            self._create_indexes()
        except PyMongoError as e:
            raise RuntimeError(f"Database initialization failed: {e}")

    def _create_indexes(self) -> None:
        try:
            self.collection.create_index([("master_id", ASCENDING)], name="idx_master_id")
        except PyMongoError as e:
            raise RuntimeError(f"Index creation failed: {e}")
    
    def create(self, node: MasterNode) -> MasterNode:
        try:
            self.collection.insert_one(node.model_dump(mode="json", by_alias=True))
            return self.get(node.master_id)
        except PyMongoError as e:
            raise RuntimeError(f"Failed to create master node: {e}")
    
    def get(self, master_id: UUID4) -> MasterNode:
        try:
            doc = self.collection.find_one({"master_id": str(master_id)})
            if not doc:
                raise MasterNodeNotFoundException(f"Master node with id {master_id} is not found")
            
            doc.pop("_id", None)
            return MasterNode(**doc)
        except PyMongoError as e:
            raise RuntimeError(f"Failed to get master node: {e}")

    def list_all(self) -> List[MasterNode]:
        try:
            docs = list(self.collection.find())
            for doc in docs:
                doc.pop("_id", None)
            return [MasterNode(**doc) for doc in docs]
        except PyMongoError as e:
            raise RuntimeError(f"Failed to list master nodes: {e}")
    
    def update(self, master_id: UUID4, updated: UpdateMasterNode) -> MasterNode:
        try:
            update_data = updated.model_dump(exclude_unset=True)
            if not update_data:
                raise ValueError("No fields to update")
            
            result = self.collection.update_one(
                {"master_id": str(master_id)},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                raise MasterNodeNotFoundException(f"Master node with id {master_id} is not found")
            return self.get(master_id)
        except PyMongoError as e:
            raise RuntimeError(f"Failed to update master node: {e}")
    
    def delete(self, master_id: UUID4) -> bool:
        try:
            result = self.collection.delete_one({"master_id": str(master_id)})
            if result.deleted_count == 0:
                raise MasterNodeNotFoundException(f"Master node with id {master_id} is not found")
            
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RuntimeError(f"Failed to delete master node: {e}")