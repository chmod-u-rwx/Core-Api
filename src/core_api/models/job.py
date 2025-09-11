from enum import Enum
from typing import Optional
from pydantic import UUID4, BaseModel, Field, HttpUrl, field_validator
from datetime import datetime

class JobStatus(str, Enum):
    paused = "paused"
    running = "running"
    completed = "completed"
    failed = "failed"

class JobResources(BaseModel):
    cpu: int = Field(..., ge=1, le=500)
    ram: int = Field(..., ge=1, le=500)

class Job(BaseModel):
    user_id: UUID4 = Field(...)
    job_id: UUID4 = Field(...)
    job_name: str = Field(..., min_length=1, max_length=100)
    job_description: str = Field(..., min_length=1, max_length=1000)
    repo_url: HttpUrl = Field(...)
    resources: JobResources = Field(...)
    status: JobStatus = Field(default=JobStatus.paused)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    
    @field_validator("repo_url")
    @classmethod
    def valudate_repo_url(cls, v: str):
        if not str(v).endswith(".git"):
            raise ValueError("repo_url must be a valid repo URL")
        
        return v
    
class JobUpdate(BaseModel):
    job_name: Optional[str] = Field(default=None)
    job_description: Optional[str] = None
    repo_url: Optional[HttpUrl] = None
    resources: Optional[JobResources] = None
    status: Optional[JobStatus] = None

class JobCreate(BaseModel):
    user_id: UUID4 = Field(...)
    job_name: str = Field(..., min_length=1, max_length=100)
    job_description: str = Field(..., min_length=1, max_length=1000)
    repo_url: HttpUrl = Field(...)
    resources: JobResources = Field(...)