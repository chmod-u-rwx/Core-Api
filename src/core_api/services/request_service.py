from datetime import datetime
from typing import List, Optional
from uuid import UUID
from ..models.requests import RequestStatus, Requests
from ..db.requests_db import RequestDatabase

class RequestService:
    def __init__(self):
        self.db = RequestDatabase()

    def list_requests(
        self,
        job_id: Optional[UUID] = None,
        worker_id: Optional[UUID] = None,
        status: Optional[RequestStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Requests]:
        return self.db.list_request(
            job_id=job_id,
            worker_id=worker_id,
            status=status,
            start_time=start_time,
            end_time=end_time
        )
    
    def count_requests(
        self,
        job_id: Optional[UUID] = None,
        worker_id: Optional[UUID] = None,
        status: Optional[RequestStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> int:
        return len(self.list_requests(job_id, worker_id, status, start_time, end_time))
    
    def get_average_execution_time(
        self,
        job_id: Optional[UUID] = None,
        worker_id: Optional[UUID] = None,
        status: Optional[RequestStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        requests = self.list_requests(job_id, worker_id, status, start_time, end_time)
        times = [r.execution_time for r in requests]
        return sum(times) / len(times) if times else 0.0

    def get_average_status_requests(
        self,
        job_id: Optional[UUID] = None,
        worker_id: Optional[UUID] = None,
        status: Optional[RequestStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> float:
        total = self.count_requests(job_id, worker_id, None, start_time, end_time)
        filtered = self.count_requests(job_id, worker_id, status, start_time, end_time)
        return (filtered / total) if total else 0.0