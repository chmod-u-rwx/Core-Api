from pydantic import BaseModel, Field
from uuid import UUID

class Node(BaseModel):
    node_id: UUID = Field(..., description="Id for node")
    job_slots: int = Field(..., gt=0, description="Number of job slots")
