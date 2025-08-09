
# Since we are using mongo db all datamodels as well as schema models 
# for mongo db will be stored here (use pydantic)

from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID

class jModel(BaseModel):
    userID: uuid4 = Field(...)
    Job_Name: str = Field(..., max_length=100)
    Job_Description : str = Field(..., max_length=500)
    Github_URL: HttpUrl = Field(..., max_length=200)
    Version: str = Field(..., max_length=50)


    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            uuid4: lambda v: str(v)
        }


