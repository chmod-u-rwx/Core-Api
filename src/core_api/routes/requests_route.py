from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from ..db.requests_db import RequestNotFoundException
from ..services.request_service import RequestService
from ..models.requests import RequestStatus, Requests

router = APIRouter(prefix="/requests", tags=["Request Metrics"])

@router.get("/", response_model=List[Requests])
def list_requests(
    job_id: Optional[UUID] = Query(None),
    status: Optional[RequestStatus] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
):
    start, end = validate_time_range(start_time, end_time)

    try:
        return RequestService().list_requests(
            job_id,
            status,
            start_time=start,
            end_time=end,
        )
        
    except RequestNotFoundException as e:
        raise HTTPException(status_code=404, detail=f"No requests found for given filters: {e}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )

@router.get("/count")
def count_requests(
    job_id: Optional[UUID] = Query(None),
    status: Optional[RequestStatus] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
):
    start, end = validate_time_range(start_time, end_time)
    
    try:
        return {"count": RequestService().count_requests(
            job_id,
            status,
            start_time=start,
            end_time=end,
        )}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )

@router.get("/average/execution-time")
def average_execution_time(
    job_id: Optional[UUID] = Query(None),
    status: Optional[RequestStatus] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
):
    start, end = validate_time_range(start_time, end_time)
    
    try:
        return {"average_execution_time": RequestService().get_average_execution_time(
            job_id,
            status,
            start_time=start,
            end_time=end,
        )}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )

@router.get("/average/status")
def average_status_requests(
    job_id: Optional[UUID] = Query(None),
    status: Optional[RequestStatus] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
):
    start, end = validate_time_range(start_time, end_time)
    
    try:
        return {"average_status": RequestService().get_average_status_requests(
            job_id,
            status,
            start_time=start,
            end_time=end,
        )}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )

def parse_datetime(dt: Optional[str]) -> Optional[datetime]:
    if dt is None:
        return None
    try:
        return datetime.fromisoformat(dt)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {dt}")

def validate_time_range(start_time: Optional[str], end_time: Optional[str]):
    start = parse_datetime(start_time)
    end = parse_datetime(end_time)
    if start and end and start > end:
        raise HTTPException(400, detail="start_time cannot be after end_time")
    return start, end