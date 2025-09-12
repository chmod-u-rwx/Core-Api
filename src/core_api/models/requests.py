from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from src.core_api.models.payloads import JobRequestPayload, JobResponsePayload

class RequestStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"

class Requests(BaseModel):
    request_id: UUID = Field(...)
    job_id: UUID = Field(...)
    worker_id: UUID = Field(...)
    vm_id: UUID = Field(...)
    request_payload: JobRequestPayload = Field(...)
    response_payload: JobResponsePayload = Field(...)
    is_success: Optional[RequestStatus] = Field(default=None)
    error_detail: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    transaction_id: Optional[UUID] = Field(default=None, description="Reference to Job expense")