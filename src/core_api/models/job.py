from pydantic import UUID4, BaseModel, Field, HttpUrl, field_validator

class Job(BaseModel):
    user_id: UUID4 = Field(..., description="Unique identifier for the user")
    job_name: str = Field(..., min_length=1, max_length=100, description="Name of the job")
    job_description: str = Field(..., min_length=1, max_length=1000, description="Description of the Job")
    github_url: HttpUrl = Field(..., description="Repo URL for the Job")
    
    @field_validator("github_url")
    @classmethod
    def valudate_github_url(cls, v: str):
        if not str(v).endswith(".git"):
            raise ValueError("github_url must be a valid repo URL")
        
        return v