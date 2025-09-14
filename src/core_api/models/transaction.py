from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, timezone
from src.core_api.models.requests import Requests

class Transaction(BaseModel):
    transaction_id: Requests = Field(..., description="Reference to the Requests model")
    job_id: UUID = Field(...)
    worker_id: UUID = Field(...)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cost_ram: float = Field(..., description="current cost of RAM (per second)")
    cost_cpu: float = Field(..., description="current cost of CPU (per second)")
    execution_time: float = Field(..., description="Execution time in seconds")
    total_cost: float = Field(...)
