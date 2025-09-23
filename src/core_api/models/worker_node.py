from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class WorkerNode(BaseModel):
    node_id: UUID = Field(..., description="Id for node")
    job_slots: int = Field(..., ge=0, description="Number of job slots")
    cpu_count: int = Field(..., ge=1, description="Number of CPUs allocated")
    memory_allocated: int = Field(..., ge=1, description="Memory allocated in MB")


class WorkerNodeUpdates(BaseModel):
    job_slots: Optional[int] = Field(default=None, description="Updated number of job slots")
    cpu_count: Optional[int] = Field(default=None, ge=1, description="Update number of CPUs allocated")
    memory_allocated: Optional[int] = Field(default=None, ge=1, description="Update memory allocated in MB")

class WorkerNodeResources(BaseModel):
    worker_id: UUID = Field(..., description="Id for worker node")
    job_slots: int = Field(..., ge=0, description="Number of job slots")
    cpu_percentage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: int = Field(..., ge=0, description="Memory usage in MB")
    memory_free: int = Field(..., ge=0, description="Free memory in MB")
    cache_used: int = Field(..., ge=0, description="Cache used in MB")
    cache_free: int = Field(..., ge=0, description="Cache free in MB")
    timestamp: datetime = Field(..., description="Timestamp of the resource report") 

