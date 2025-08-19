from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class Node(BaseModel):
    node_id: UUID = Field(..., description="Id for node")
    job_slots: int = Field(..., ge=0, description="Number of job slots")
    cpu_count: int = Field(..., ge=1, description="Number of CPUs allocated")
    memory_allocated: int = Field(..., ge=1, description="Memory allocated in MB")

class NodeUpdates(BaseModel):
    job_slots: int = Field(..., description="Updated number of job slots")
    cpu_count: Optional[int] = Field(None, ge=1, description="Update number of CPUs allocated")
    memory_allocated: Optional[int] = Field(None, ge=1, description="Update memory allocated in MB")
