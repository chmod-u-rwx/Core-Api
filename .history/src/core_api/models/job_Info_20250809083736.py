
# Since we are using mongo db all datamodels as well as schema models 
# for mongo db will be stored here (use pydantic)

from pydantic import BaseModel, Field, HttpUrl, UUID4

class jobmodel(BaseModel):
    userID: UUID4 = Field(...)
    Job_Name: str = Field(..., max_length=100)
    Job_Description : str = Field(..., max_length=500)
    github_URL: HttpUrl = Field(..., max_length=200)
    Version: str = Field(..., max_length=50)

