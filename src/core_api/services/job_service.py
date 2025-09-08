from typing import List, Optional, Union
from uuid import UUID, uuid4
from pydantic import UUID4
from src.core_api.db.job_db import JobDatabase
from src.core_api.models.job import Job, JobStatus, JobUpdate, JobCreate
from datetime import datetime, timezone

class JobService:
    def __init__(self) -> None:
        self.db = JobDatabase()
        
    def create_job(self, create_job: JobCreate) -> Job:
        job_id = uuid4()
        now = datetime.now(timezone.utc)
        job = Job(
            user_id=create_job.user_id,
            job_id=job_id,
            job_name=create_job.job_name,
            job_description=create_job.job_description,
            repo_url=create_job.repo_url,
            resources=create_job.resources,
            status=JobStatus.pending,
            created_at=now,
            updated_at=now,
        )
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