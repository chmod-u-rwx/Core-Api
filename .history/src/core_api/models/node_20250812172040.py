from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    id: Optional
    job_slots: int