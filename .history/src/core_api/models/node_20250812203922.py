from pydantic import BaseModel
from uuid import uuid4

class Node(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_slots: int