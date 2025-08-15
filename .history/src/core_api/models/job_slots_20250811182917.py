from pydantic import BaseModel 

class Job(BaseModel):
    job_slots: str
