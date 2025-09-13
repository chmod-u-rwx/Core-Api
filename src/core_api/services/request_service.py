from datetime import datetime
from typing import List, Optional
from uuid import UUID
from src.core_api.models.requests import RequestStatus, Requests
from src.core_api.db.requests_db import RequestDatabase

class RequestService:
    def __init__(self):
        self.db = RequestDatabase()

    def list_requests(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Requests]:
        return self.db.list_request(
            job_id=job_id,
            start_time=start_time,
            end_time=end_time
        )
    
    def list_successful_requests(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Requests]:
        return self.db.list_request(
            job_id=job_id,
            status=RequestStatus.SUCCESS,
            start_time=start_time,
            end_time=end_time
        )
    
    def list_failed_requests(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Requests]:
        return self.db.list_request(
            job_id=job_id,
            status=RequestStatus.FAILED,
            start_time=start_time,
            end_time=end_time
        )
    
    def count_requests(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> int:
        return len(self.list_requests(job_id, start_time, end_time))
    
    def count_success(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> int:
        return len(self.list_successful_requests(job_id, start_time, end_time))
    
    def count_failed(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> int:
        return len(self.list_failed_requests(job_id, start_time, end_time))
    
    def average_execution_time(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        requests = self.list_requests(job_id, start_time, end_time)
        times = [r.execution_time for r in requests]
        return sum(times) / len(times) if times else 0.0
    
    def average_success_requests(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        total = self.count_requests(job_id, start_time, end_time)
        success = self.count_success(job_id, start_time, end_time)
        return (success / total) if total else 0.0
    
    def average_failed_requests(
        self,
        job_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        total = self.count_requests(job_id, start_time, end_time)
        failed = self.count_failed(job_id, start_time, end_time)
        return (failed / total) if total else 0.0