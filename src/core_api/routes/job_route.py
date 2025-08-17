from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import UUID4
from src.core_api.db.job_db import JobNotFoundException
from src.core_api.services.job_service import JobService
from src.core_api.models.job import Job, JobCreate, JobUpdate

router = APIRouter(prefix="/job", tags=["Jobs"])

@router.post("/create", response_model=Job)
def create_job(create_job: JobCreate):
    try:
        return JobService().create_job(create_job)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/get/{job_id}", response_model=Job)
def get_job(job_id: UUID4):
    try:
        return JobService().get_job(job_id)
    except JobNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/list", response_model=List[Job])
def list_job(
    user_id: Optional[UUID4] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1),
    newest_first: bool = Query(True)
):
    if limit < 1:
        raise HTTPException(
            status_code=422,
            detail="Parameter 'limit' must be greater than or equal to 1. This is required for pagination and to avoid accidental performance issues."
        )
    return JobService().list_job(user_id, skip, limit, newest_first)

@router.put("/update/{job_id}", response_model=Job)
def update_job(job_id: UUID4, update_data: JobUpdate):
    try:
        return JobService().update_job(job_id, update_data)
    except JobNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
@router.delete("/delete/{job_id}")
def delete_job(job_id: UUID4):
    try:
        return JobService().delete_job(job_id)
    except JobNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))