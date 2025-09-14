from datetime import datetime, timezone
from uuid import uuid4
import pytest
from typing import Any
from unittest.mock import patch
from mongomock import MongoClient

from src.core_api.models.payloads import JobRequestPayload, JobResponsePayload
from src.core_api.models.requests import RequestStatus, Requests
from src.core_api.db.requests_db import RequestDatabase, RequestNotFoundException

@pytest.fixture
def requests_db():
    with patch("src.core_api.db.requests_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = MongoClient()
        mock_get_client.return_value = mock_client
        
        db = RequestDatabase()
        yield db

def make_request(status: RequestStatus = RequestStatus.SUCCESS):
    req_id = uuid4()
    job_id = uuid4()
    worker_id = uuid4()
    vm_id = uuid4()
    transaction_id = uuid4()
    now = datetime.now(timezone.utc)
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
        timestamp=now,
        execution_time=1.23,
        transaction_id=transaction_id
    )

def test_create_and_get_request(requests_db: RequestDatabase):
    req = make_request()
    created = requests_db.create(req)
    assert created.request_id == req.request_id
    
    fetched = requests_db.get(req.request_id)
    assert fetched.request_id == req.request_id

def test_list_request_filters(requests_db: RequestDatabase):
    req_success = make_request(RequestStatus.SUCCESS)
    req_failed = make_request(RequestStatus.FAILED)
    
    requests_db.create(req_success)
    requests_db.create(req_failed)
    all_reqs = requests_db.list_request()
    assert len(all_reqs) == 2
    
    success_reqs = requests_db.list_request(status=RequestStatus.SUCCESS)
    assert len(success_reqs) == 1
    assert success_reqs[0].status == RequestStatus.SUCCESS
    
    failed_reqs = requests_db.list_request(status=RequestStatus.FAILED)
    assert len(failed_reqs) == 1
    assert failed_reqs[0].status == RequestStatus.FAILED

def test_delete_request(requests_db: RequestDatabase):
    req = make_request()
    requests_db.create(req)
    assert requests_db.delete(req.request_id) is None
    with pytest.raises(RequestNotFoundException):
        requests_db.get(req.request_id)

def test_get_not_found(requests_db: RequestDatabase):
    with pytest.raises(RequestNotFoundException):
        requests_db.get(uuid4())

def test_delete_not_found(requests_db: RequestDatabase):
    with pytest.raises(RequestNotFoundException):
        requests_db.delete(uuid4())