from pydantic import BaseModel, Field
from uuid import uuid4


class Node(BaseModel):
    node_id: str = Field()
    job_slots: int = Field(..., ge=0, description="Job slots on the node")
