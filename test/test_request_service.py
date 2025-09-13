from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from unittest.mock import patch
from uuid import UUID, uuid4
import pytest
from mongomock import MongoClient

from src.core_api.models.payloads import JobRequestPayload, JobResponsePayload
from src.core_api.models.requests import RequestStatus, Requests
from src.core_api.services.request_service import RequestService

@pytest.fixture
def request_service():
    with patch("src.core_api.db.requests_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = MongoClient()
        mock_get_client.return_value = mock_client
        
        yield RequestService()

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

def test_list_and_count_requests(request_service: RequestService):
    now = datetime.now(timezone.utc)
    req1 = make_request(status=RequestStatus.SUCCESS, exec_time=2.0, timestamp=now)
    req2 = make_request(status=RequestStatus.FAILED, exec_time=1.0, timestamp=now)
    req3 = make_request(status=RequestStatus.SUCCESS, exec_time=3.0, timestamp=now)
    
    request_service.db.create(req1)
    request_service.db.create(req2)
    request_service.db.create(req3)
    
    all_requests = request_service.list_requests()
    assert len(all_requests) == 3
    
    success_requests = request_service.list_successful_requests()
    assert len(success_requests) == 2
    
    failed_requests = request_service.list_failed_requests()
    assert len(failed_requests) == 1
    
    assert request_service.count_requests() == 3
    assert request_service.count_success() == 2
    assert request_service.count_failed() == 1

def test_average_execution_time(request_service: RequestService):
    now = datetime.now(timezone.utc)
    req1 = make_request(status=RequestStatus.SUCCESS, exec_time=2.0, timestamp=now)
    req2 = make_request(status=RequestStatus.FAILED, exec_time=4.0, timestamp=now + timedelta(seconds=5))
    request_service.db.create(req1)
    request_service.db.create(req2)
    
    avg_time = request_service.average_execution_time()
    assert avg_time == 3.0

def test_average_success_and_failed(request_service: RequestService):
    now = datetime.now(timezone.utc)
    req1 = make_request(status=RequestStatus.SUCCESS, exec_time=1.0, timestamp=now)
    req2 = make_request(status=RequestStatus.FAILED, exec_time=1.0, timestamp=now)
    req3 = make_request(status=RequestStatus.SUCCESS, exec_time=1.0, timestamp=now)
    
    request_service.db.create(req1)
    request_service.db.create(req2)
    request_service.db.create(req3)
    
    avg_success = request_service.average_success_requests()
    avg_failed = request_service.average_failed_requests()
    assert avg_success == 2/3
    assert avg_failed == 1/3

def test_list_request_with_all_filters(request_service: RequestService):
    job_id = uuid4()
    now = datetime.now(timezone.utc)
    
    req1 = make_request(
        status=RequestStatus.SUCCESS,
        exec_time=1.0,
        timestamp=now,
        job_id=job_id
    )
    req2 = make_request(
        status=RequestStatus.FAILED,
        exec_time=1.0, 
        timestamp=now,
        job_id=uuid4(),
    )
    req3 = make_request(
        status=RequestStatus.SUCCESS,
        exec_time=1.0,
        timestamp=now,
        job_id=job_id
    )
    
    request_service.db.create(req1)
    request_service.db.create(req2)
    request_service.db.create(req3)
    
    start = now
    end = now + timedelta(minutes=1, seconds=30)
    
    filtered = request_service.list_requests(
        job_id=job_id,
        start_time = start,
        end_time = end,
    )
    assert len(filtered) == 2
    
    filtered_success = request_service.list_successful_requests(
        job_id=job_id,
        start_time = start,
        end_time = end,
    )
    assert len(filtered_success) == 2
    assert all(req.status == RequestStatus.SUCCESS for req in filtered_success)
    
    filtered_failed = request_service.list_failed_requests(
        job_id=job_id,
        start_time = start,
        end_time = end,
    )
    assert len(filtered_failed) == 0