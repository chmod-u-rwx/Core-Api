from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    id: Optional[str]=Field(alias="_id")
    job_slots: int