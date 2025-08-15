from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    job_slots: int = Field(gt = 0, description="Number of job slots available on the node")