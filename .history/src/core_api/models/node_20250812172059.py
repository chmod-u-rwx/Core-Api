from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    id: Optional[str]=Field(alias="")
    job_slots: int