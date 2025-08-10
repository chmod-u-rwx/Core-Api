from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from pydantic import UUID4
from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from .utils import serialize_job, to_get_object_id
from .connection import get_mongo_client
from ..models.job import Job
from ..config import DATABASE_NAME

class JobInDB(Job):
    id: str
    created_at: datetime
    updated_at: datetime
    
class JobDatabase:
    def __init__(
        self,
        client: Any | None = None,
        db_name: str = DATABASE_NAME,
        collection_name: str = "jobs",
        ) -> None:
            self.client = client or get_mongo_client()
            self.db: Database[Any] = self.client[db_name]
            self.collection: Collection[Any] = self.db[collection_name]
            self._ensure_indexes()
            
    # Index for queries by user_id
    def _ensure_indexes(self) -> None:
        self.collection.create_index([("user_id", ASCENDING)], name="idx_user_id")   
    
    #  --- CRUD Operations ---
    def create_job(self, job: Job) -> JobInDB:
        now = datetime.now(timezone.utc)
        doc = serialize_job(job) 
        doc.update({"created_at": now, "updated_at": now})
        
        try:
            result = self.collection.insert_one(doc)
        except PyMongoError as e:
            raise RuntimeError(f"MongoDB insertion failed: {e}") from e
        
        inserted = self.collection.find_one({"_id": result.inserted_id})
        assert inserted is not None
        return self._to_job_in_db(inserted)
    
    def get_job(self, job_id: str) -> Optional[JobInDB]:
        obj_id = to_get_object_id(job_id)
        doc = self.collection.find_one({"_id": obj_id})
        if not doc:
            return None
        return self._to_job_in_db(doc)
    
    def list_jobs(
        self,
        user_id: Optional[UUID4],
        skip: int = 0,
        limit: int = 50,
        newest_first: bool = True
    ) -> List[JobInDB]:
        query: Dict[str, Any] = {}
        
        if user_id is not None:
            query["user_id"] = str(user_id)
            
        get_query = (
            self.collection.find(query)
            .sort("created_at", DESCENDING if newest_first else ASCENDING)
            .skip(max(0, skip))
            .limit(max(0, limit))
        )
        
        return [self._to_job_in_db(doc) for doc in get_query]
    
    def update_job(self, job_id: str, updates: Dict[str, Any]) -> Optional[JobInDB]:
        allowed = {"job_name", "job_description", "repo_url"}
        disallowed = set(updates.keys()) - allowed
        
        if disallowed:
            raise ValueError(f"Updates are not allowed on fields: {', '.join(sorted(disallowed))}")
        
        obj_id = to_get_object_id(job_id)
        current = self.collection.find_one({"_id": obj_id})
        
        if not current:
            return None
        
        current_job = Job(
            user_id=current["user_id"],
            job_name=current["job_name"],
            job_description=current["job_description"],
            repo_url=current["repo_url"],
        )
        
        # Updated the current validated data (Job Model)
        updated_job = Job(
            user_id=current_job.user_id,
            job_name=updates.get("job_name", current_job.job_name),
            job_description=updates.get("job_description", current_job.job_description),
            repo_url=updates.get("repo_url", current_job.repo_url),
        )
        
        update_doc = serialize_job(updated_job)
        update_doc["updated_at"] = datetime.now(timezone.utc)
        
        try:
            self.collection.update_one({"_id": obj_id}, {"$set": update_doc})
        except PyMongoError as e:
            raise RuntimeError(f"MongoDB update failed: {e}") from e
        
        updated = self.collection.find_one({"_id": obj_id})
        assert updated is not None
        return self._to_job_in_db(updated)
    
    def delete_job(self, job_id: str) -> bool:
        obj_id = to_get_object_id(job_id)
        try:
            result = self.collection.delete_one({"_id": obj_id})
        except PyMongoError as e:
            raise RuntimeError(f"MongoDB deletion failed: {e}") from e
        
        return result.deleted_count == 1
    
    @staticmethod
    def _to_job_in_db(doc: Dict[str, Any]) -> JobInDB:
        return JobInDB(
            id=str(doc["_id"]),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            user_id=doc["user_id"],
            job_name=doc["job_name"],
            job_description=doc["job_description"],
            repo_url=doc["repo_url"]
        )