
# Since we are using mongo db all datamodels as well as schema models 
# for mongo db will be stored here (use pydantic)

from pydantic import BaseModel, Field, HttpUrl, UUID4

class jobmodel(BaseModel):
    userid: UUID4 = Field(...)
    job_name: str = Field(..., max_length=100)
    job_Description : str = Field(..., max_length=500)
    github_url: HttpUrl = Field(..., max_length=200)
    Version: str = Field(..., max_length=50)

