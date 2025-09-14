import pytest
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from unittest.mock import patch
from uuid import UUID, uuid4
from fastapi.testclient import TestClient
from mongomock import MongoClient
from src.core_api.services.request_service import RequestService
from src.core_api.models.payloads import JobRequestPayload, JobResponsePayload
from src.core_api.models.requests import RequestStatus, Requests
from src.core_api.app import app

@pytest.fixture
def client():
    with patch("src.core_api.db.requests_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = MongoClient()
        mock_get_client.return_value = mock_client
        yield TestClient(app)

def make_request(
    status: RequestStatus,
    exec_time: float,
    timestamp: datetime,
    job_id: Optional[UUID] = None
):
    req_id = uuid4()
    job_id = job_id or uuid4()
    worker_id = uuid4()
    vm_id = uuid4()
    transaction_id = uuid4()
    return Requests(
        request_id=req_id,
        job_id=job_id,
        worker_id=worker_id,
        vm_id=vm_id,
        request_payload=JobRequestPayload(
            request_id=req_id,
            job_id=job_id,
            master_id=uuid4(),
            worker_id=uuid4(),
            path="",
            method=None,
            headers={},
            params={},
            body={"data": "test"}
        ),
        response_payload=JobResponsePayload(
            request_id=req_id,
            job_id=job_id,
            master_id=uuid4(),
            worker_id=uuid4(),
            status_code=200,
            meta={},
            headers={},
            body={"data", "test"},
        ),
        status=status,
        timestamp=timestamp,
        execution_time=exec_time,
        transaction_id=transaction_id
    )

# Insert test data using request_service
def insert_requests():
    now = datetime.now(timezone.utc)
    job_id = uuid4()
    requests = [
        make_request(
            status=RequestStatus.SUCCESS,
            exec_time=2.0,
            timestamp=now,
            job_id=job_id
        ),
        make_request(
            status=RequestStatus.SUCCESS,
            exec_time=4.0,
            timestamp=now + timedelta(minutes=1),
            job_id=job_id
        ),
        make_request(
            status=RequestStatus.FAILED,
            exec_time=3.0,
            timestamp=now + timedelta(minutes=2),
            job_id=uuid4()
        ),
    ]
    
    for request in requests:
        RequestService().db.create(request)
    
    return job_id, now

def test_list_all_requests(client: Any):
    insert_requests()
    response = client.get("/requests/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3

def test_list_successful_requests(client: Any):
    insert_requests()
    response = client.get(f"/requests/?status=success")
    assert response.status_code == 200
    
    data = response.json()
    assert all(r["status"] == "success" for r in data)
    assert len(data) == 2

def test_list_failed_requests(client: Any):
    insert_requests()
    response = client.get(f"/requests/?status=failed")
    assert response.status_code == 200
    
    data = response.json()
    assert all(r["status"] == "failed" for r in data)
    assert len(data) == 1

def test_timeframe_and_job_id_filtering(client: Any):
    job_id, now = insert_requests()
    start = now.isoformat()
    end = (now + timedelta(minutes=1, seconds=30)).isoformat()
    response = client.get(
        "/requests/",
        params={
            "job_id": str(job_id),
            "start_time": start,
            "end_time": end,
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all(r["job_id"] == str(job_id) for r in data)

def test_count_requests(client: Any):
    insert_requests()
    response = client.get("/requests/count")
    assert response.status_code == 200
    assert response.json()["count"] == 3

def test_count_success(client: Any):
    insert_requests()
    response = client.get("/requests/count?status=success")
    assert response.status_code == 200
    assert response.json()["count"] == 2

def test_count_failed(client: Any):
    insert_requests()
    response = client.get("/requests/count?status=failed")
    assert response.status_code == 200
    assert response.json()["count"] == 1

def test_average_execution_time(client: Any):
    insert_requests()
    response = client.get("/requests/average/execution-time")
    assert response.status_code == 200
    
    avg = response.json()["average_execution_time"]
    assert avg == pytest.approx((2.0 + 4.0 + 3.0) / 3) # type: ignore

def test_average_status_success(client: Any):
    insert_requests()
    response = client.get("/requests/average/status?status=success")
    assert response.status_code == 200
    avg = response.json()["average_status"]
    assert avg == pytest.approx(2 / 3) #type: ignore

def test_average_status_failed(client: Any):
    insert_requests()
    response = client.get("/requests/average/status?status=failed")
    assert response.status_code == 200
    avg = response.json()["average_status"]
    assert avg == pytest.approx(1 / 3) #type: ignore