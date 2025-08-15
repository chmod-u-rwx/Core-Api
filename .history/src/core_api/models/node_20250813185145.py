from pydantic import BaseModel, Field
from uuid import uuid4

class Node(BaseModel):
    node_id: str = Field(default_factory=lambda: str(uuid4()), description="Id for node")
    job_slots: int = Field(..., ge=0, description="Job slots on the node")

    @validator('node_id')
    def node_id_must_not_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("node_id cannot be empty or whitespace")
        return v