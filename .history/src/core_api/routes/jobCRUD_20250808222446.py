from fastapi import APIRouter
from ..services.sample import jService
from ..models.jobInfo import jModel
from uuid import uuid4

router = APIRouter(prefix="/jobs")

#Create
@router.post("/", summary="Create a new job")
async def create_job(job: jModel) -> dict[str, Any]:
    # TODO: Insert into MongoDB
    return {"message": "Job created", "job": job}

# READ
@router.get("/{job_id}", summary="Get job by ID")
async def get_job(job_id: UUID):
    # TODO: Fetch from MongoDB
    return {"message": "Job fetched", "job_id": str(job_id)}

# UPDATE
@router.put("/{job_id}", summary="Update a job by ID")
async def update_job(job_id: UUID, job: jModel):
    # TODO: Update job in MongoDB
    return {"message": "Job updated", "job_id": str(job_id), "job": job}

# DELETE
@router.delete("/{job_id}", summary="Delete a job by ID")
async def delete_job(job_id: UUID):
    # TODO: Delete from MongoDB
    return {"message": "Job deleted", "job_id": str(job_id)}