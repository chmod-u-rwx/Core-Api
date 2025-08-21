from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from uuid import UUID

from pydantic import UUID4
from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from .connection import get_mongo_client
from ..models.job import Job, JobUpdate
from ..config import DATABASE_NAME

class JobNotFoundException(Exception):
    ...
    
class JobDatabase:
    def __init__(
        self,
        ) -> None:
            self.client = get_mongo_client()
            self.db: Database[Any] = self.client[DATABASE_NAME]
            self.collection: Collection[Any] = self.db["jobs"]
            self._create_indexes()
            
    # Index for queries by user_id
    def _create_indexes(self) -> None:
        self.collection.create_index([("user_id", ASCENDING)], name="idx_user_id")   
    
    #  --- CRUD Operations ---
    def create(self, job: Job) -> Job:
        doc = job.model_dump(mode='json', by_alias=True, exclude_unset=True)
        doc.update({
            "user_id": str(job.user_id),
            "job_id": str(job.job_id),
            "created_at": str(job.created_at),
            "updated_at": str(job.updated_at)
        })
        
        try:
            result = self.collection.insert_one(doc)
        except PyMongoError as e:
            raise RuntimeError(f"MongoDB insertion failed: {e}") from e

        inserted = self.collection.find_one({"_id": result.inserted_id})
        assert inserted is not None
        
        inserted.pop("_id", None)
        
        return Job(**inserted)
    
    def get(self, job_id: UUID4) -> Job:
        doc = self.collection.find_one({"job_id": str(job_id)})
        if not doc:
            raise JobNotFoundException(f"Job with id {job_id} not found")
        
        return Job(**doc)
    
    def list_all(
        self,
        user_id: Optional[UUID4],
        skip: int = 0,
        limit: int = 50,
        newest_first: bool = True
    ) -> List[Job]:
        query: Dict[str, Any] = {}
        
        if user_id is not None:
            query["user_id"] = str(user_id)
            
        get_query = (
            self.collection.find(query)
            .sort("created_at", DESCENDING if newest_first else ASCENDING)
            .skip(max(0, skip))
            .limit(max(0, limit))
        )
        
        return [Job(**doc) for doc in get_query]
    
    def update(self, job_id: UUID4, update_data: JobUpdate) -> Job:
        current = self.collection.find_one({"job_id": str(job_id)})
        if not current:
            raise JobNotFoundException(f"Job with id {job_id} not found")

        update_fields = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if not update_fields:
            raise ValueError("No valid fields to update.")
        
        update_fields["updated_at"] = datetime.now(timezone.utc)
        
        try:
            result = self.collection.update_one({"job_id": str(job_id)}, {"$set": update_fields})
            if result.matched_count == 0:
                raise JobNotFoundException(f"Job with id {job_id} not found")
        except PyMongoError as e:
            raise RuntimeError(f"MongoDB update failed: {e}") from e
        
        updated = self.collection.find_one({"job_id": str(job_id)})
        assert updated is not None
        
        return Job(**updated)
    
    def delete(self, job_id: Union[str, UUID]) -> bool:
        if isinstance(job_id, UUID):
            job_id_str = str(job_id)
        else:
            # Validate string is a valid UUID
            try:
                UUID(job_id)
                job_id_str = job_id
            except ValueError:
                raise ValueError(f"Invalid job_id format: {job_id}")
        
        try:
            result = self.collection.delete_one({"job_id": job_id_str})
            if result.deleted_count == 0:
                raise JobNotFoundException(f"Job with id {job_id_str} not found")
        except PyMongoError as e:
            raise RuntimeError(f"MongoDB deletion failed: {e}") from e
        
        return result.deleted_count == 1    