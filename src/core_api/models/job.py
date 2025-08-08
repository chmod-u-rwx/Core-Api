from pydantic import UUID4, BaseModel, Field, HttpUrl, field_validator

class Job(BaseModel):
    user_id: UUID4 = Field(...)
    job_name: str = Field(..., min_length=1, max_length=100)
    job_description: str = Field(..., min_length=1, max_length=1000)
    repo_url: HttpUrl = Field(...)
    
    @field_validator("repo_url")
    @classmethod
    def valudate_github_url(cls, v: str):
        if not str(v).endswith(".git"):
            raise ValueError("repo_url must be a valid repo URL")
        
        return v