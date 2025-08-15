from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    job_slots: int = Field(gt)