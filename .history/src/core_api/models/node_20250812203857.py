from pydantic import BaseModel

class Node(BaseModel):
    
    job_slots: int