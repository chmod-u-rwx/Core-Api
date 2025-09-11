from typing import Any
from unittest.mock import patch
from uuid import uuid4
from src.core_api.models.job import JobResources, JobUpdate, JobCreate
from src.core_api.db.job_db import JobDatabase, JobNotFoundException
from src.core_api.services.job_service import JobService
import mongomock
from mongomock import MongoClient
import pytest

@pytest.fixture
def job_db():
    with patch("src.core_api.db.job_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        
        db = JobDatabase()
        yield db

@pytest.fixture
def job_service(job_db: JobDatabase):
    service=JobService()
    service.db=job_db
    return service
        
def test_create_valid_job(job_service: JobService):
    job_create = JobCreate(
        user_id=uuid4(),
        job_name="Test Job",
        job_description="A description",
        resources=JobResources(cpu=2, ram=4),
        repo_url="https://github.com/example.repo.git" # type: ignore
    )
    created = job_service.create_job(job_create)
    assert created.job_name == "Test Job"
    
def test_create_missing_fields(job_service: JobService):
    with pytest.raises(Exception):
        job_create = JobCreate(
        user_id=uuid4(),
        job_name="",
        job_description="",
        resources=JobResources(cpu=0, ram=0),
        repo_url="https://github.com/example.repo.git" # type: ignore
    )
        job_service.create_job(job_create)
        
def test_get_job_success(job_service: JobService):
    job_create = JobCreate(
        user_id=uuid4(),
        job_name="Get Name Test",
        job_description="A description",
        resources=JobResources(cpu=2, ram=4),
        repo_url="https://github.com/example.repo.git" # type: ignore
    )
    
    created=job_service.create_job(job_create)
    fetched = job_service.get_job(created.job_id)
    assert fetched.job_name == "Get Name Test", "Didn't get job_name"
        
def test_get_job_not_found(job_service: JobService):
    fake_id = uuid4()
    
    with pytest.raises(JobNotFoundException):
        job_service.get_job(fake_id)
        assert fake_id is None
    
def test_valid_update_job(job_service: JobService):
    job_create = JobCreate(
        user_id=uuid4(),
        job_name="Test Job",
        job_description="A description",
        resources=JobResources(cpu=2, ram=4),
        repo_url="https://github.com/example.repo.git" # type: ignore
    )
    
    created=job_service.create_job(job_create)
    update = JobUpdate(job_name="New Job")
    updated_job = job_service.update_job(created.job_id, update)
    
    assert updated_job.job_name == "New Job", "job_name has not been updated"
    
def test_update_not_found(job_service: JobService):
    update = JobUpdate(job_name="Update Not Found")
    fake_id = uuid4()
    
    with pytest.raises(JobNotFoundException):
        job_service.update_job(fake_id, update)
    
def test_list_all__empty_job(job_service: JobService):
    jobs = job_service.list_job()
    assert jobs == [], "All Job is not listed"
    
def test_list_all_non_empty_job(job_service: JobService):
    job_create = JobCreate(
        user_id=uuid4(),
        job_name="Test Job",
        job_description="A description",
        resources=JobResources(cpu=2, ram=4),
        repo_url="https://github.com/example.repo.git" # type: ignore
    )
    
    job_service.create_job(job_create)
    jobs = job_service.list_job()
    
    assert len(jobs) == 1
    assert jobs[0].job_name == "Test Job"
    
def test_delete_job(job_service: JobService):
    job_create = JobCreate(
        user_id=uuid4(),
        job_name="Test Job",
        job_description="A description",
        resources=JobResources(cpu=2, ram=4),
        repo_url="https://github.com/example.repo.git" # type: ignore
    )
    
    created = job_service.create_job(job_create)
    
    deleted = job_service.delete_job(created.job_id)
    assert deleted is True, "Job has not deleted"
    
    with pytest.raises(JobNotFoundException):
        assert job_service.get_job(created.job_id) is None
        
def test_delete_job_not_found(job_service: JobService):
    fake_id = str(uuid4())
    with pytest.raises(JobNotFoundException):
        assert job_service.delete_job(fake_id)