from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    id: Optional[str]=Field
    job_slots: int