from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID
from src.core_api.models.requests import RequestStatus, Requests
from src.core_api.config import DATABASE_NAME
from src.core_api.db.connection import get_mongo_client
from pymongo.errors import PyMongoError
from pymongo.database import Database
from pymongo.collection import Collection

class RequestNotFoundException(Exception):
    ...

class RequestDatabase:
    def __init__(
        self
    ) -> None:
        try:
            self.client = get_mongo_client()
            self.db: Database[Any] = self.client[DATABASE_NAME]
            self.collection: Collection[Any] = self.db["requests"]
            self._create_indexes()
        except PyMongoError as e:
            raise RuntimeError(f"Database initialization failed: {e}")
    
    def _create_indexes(self) -> None:
        try:
            self.collection.create_index(
                [("request_id", 1)],
                name="idx_request_id",
                unique=True,
            )
            self.collection.create_index(
                [("job_id", 1)],
                name="idx_job_id",
            )
            self.collection.create_index(
                [("timestamp", 1)],
                name="idx_timestamp"
            )
        except PyMongoError as e:
            raise RuntimeError(f"Index creation failed: {e}")
    
    def create(self, request: Requests) -> Requests:
        doc = request.model_dump(mode="json", by_alias=True)
        try:
            result = self.collection.insert_one(doc)
            if not result.inserted_id:
                raise RuntimeError("Failed to insert request")
            
            inserted = self.collection.find_one({"_id": result.inserted_id})
            if not inserted:
                raise RuntimeError("Inserted requests not found")
            inserted.pop("_id", None)
            
            return Requests(**inserted)
        except PyMongoError as e:
            raise RuntimeError(f"Failed to create request: {e}")
    
    def get(self, request_id: UUID) -> Requests:
        doc = self.collection.find_one({"request_id": str(request_id)})
    
        if not doc:
            raise RequestNotFoundException(f"Request {request_id} not found")
        doc.pop("_id", None)
        return Requests(**doc)
    
    def list_request(
        self,
        job_id: Optional[UUID] = None,
        request_status: Optional[RequestStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Requests]:
        query = {}
        
        if job_id:
            query["job_id"] = job_id
        
        if request_status is not None:
            query["status"] = request_status
        
        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time
            
            if end_time:
                query["timestamp"]["$lte"] = end_time
        
        docs = list(self.collection.find(query))
        
        for doc in docs:
            doc.pop("_id", None)
        
        return [Requests(**doc) for doc in docs]
    
    def delete(self, request_id: UUID):
        try:
            result = self.collection.delete_one({"request_id": str(request_id)})
            if result.deleted_count == 0:
                raise RequestNotFoundException(f"Request with an id: {request_id} is not found")
        except PyMongoError as e:
            raise RuntimeError(f"Failed to delete request: {e}")