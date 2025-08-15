from pydantic import BaseModel, Field
from uuid import uuid4


class Node(BaseModel):
    node_id: str = Field(default_factory=lambda: str(uuid4()), description="Id for node",)
    job_slots: int = Field(..., ge=0, description="Job slots on the node")
