from pydantic import BaseModel

class Node(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_slots: int