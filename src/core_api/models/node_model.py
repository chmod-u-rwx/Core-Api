from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Node(BaseModel):
    node_id: UUID = Field(default_factory=uuid4)
    job_slots: int = Field(..., gt=0, description="Number of job slots")
