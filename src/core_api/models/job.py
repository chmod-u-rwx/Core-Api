from typing import Optional
from pydantic import UUID4, BaseModel, Field, HttpUrl, field_validator
from datetime import datetime

class Job(BaseModel):
    user_id: UUID4 = Field(...)
    job_id: UUID4 = Field(...)
    job_name: str = Field(..., min_length=1, max_length=100)
    job_description: str = Field(..., min_length=1, max_length=1000)
    repo_url: HttpUrl = Field(...)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    
    @field_validator("repo_url")
    @classmethod
    def valudate_repo_url(cls, v: str):
        if not str(v).endswith(".git"):
            raise ValueError("repo_url must be a valid repo URL")
        
        return v
    
class JobUpdate(BaseModel):
    job_name: Optional[str] = None
    job_description: Optional[str] = None
    repo_url: Optional[HttpUrl] = None