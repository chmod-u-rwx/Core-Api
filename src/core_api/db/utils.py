from typing import Any, Dict
from bson import ObjectId
from bson.errors import InvalidId

from ..models.job import Job

# --- Helper functions for Job Database ---
def serialize_job(job: Job) -> Dict[str, Any]:
    """
    Converts entities into string since 
    MongoDB doesn't natively supports UUID and HttpUrl
    """
    return {
        "user_id": str(job.user_id),
        "job_name": str(job.job_name),
        "job_description": str(job.job_description),
        "repo_url": str(job.repo_url)
    }
    
def to_get_object_id(job_id: str) -> ObjectId:
    try:
        return ObjectId(job_id)
    except (InvalidId, TypeError) as e:
        raise ValueError("Invalid job_id format") from e