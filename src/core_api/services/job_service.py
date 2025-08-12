from typing import List, Optional, Union
from uuid import UUID
from pydantic import UUID4
from src.core_api.db.job_db import JobDatabase
from src.core_api.models.job import Job, JobUpdate

class JobService:
    def __init__(self) -> None:
        self.db = JobDatabase()
        
    def create_job(self, job: Job) -> Job:
        return self.db.create(job)
    
    def get_job(self, job_id: UUID4) -> Job:
        return self.db.get(job_id)
    
    def list_job(
        self,
        user_id: Optional[UUID4] = None,
        skip: int = 0,
        limit: int = 50,
        newest_first: bool = True
    ) -> List[Job]:
        return self.db.list_all(user_id, skip, limit, newest_first)
    
    def update_job(self, job_id: UUID4, update_data: JobUpdate) -> Job:
        return self.db.update(job_id, update_data)
    
    def delete_job(self, job_id: Union[str, UUID]) -> bool:
        return self.db.delete(job_id)