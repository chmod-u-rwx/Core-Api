from pydantic import BaseModel 

class Job(BaseModel):
    user_id: str
