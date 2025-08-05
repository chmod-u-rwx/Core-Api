
# Since we are using mongo db all datamodels as well as schema models 
# for mongo db will be stored here (use pydantic)

from pydantic import UUID4, BaseModel, Field

class SampleModel(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(...)



