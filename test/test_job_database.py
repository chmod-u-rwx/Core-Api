from typing import Any
from pydantic import UUID4, HttpUrl, ValidationError
import pytest
from pytest import MonkeyPatch
from pymongo.errors import PyMongoError
from uuid import uuid4
from mongomock import MongoClient
import mongomock
from src.core_api.db.job_db import JobDatabase, JobNotFoundException
from src.core_api.models.job import Job
from unittest.mock import patch

@pytest.fixture
def job_db():
    with patch("src.core_api.db.job_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        
        db = JobDatabase()
        yield db
    
    
def make_job(
        user_id: UUID4, 
        job_id: UUID4,     
    ):
        return Job(
            user_id=user_id,
            job_id=job_id,
            job_name = "Borrow Ram Power", 
            job_description = "Temporary RAM boost", 
            repo_url = "https://github.com/example/repo.git", # type: ignore
            created_at=None,
            updated_at=None,
        )
    
def test_create_job_returns_job_in_db(job_db: JobDatabase):
    user_id = uuid4()
    job_id = uuid4()
    created = job_db.create(make_job(user_id, job_id))
    
    assert created.user_id == user_id
    assert created.job_id == job_id
    assert created.job_name == "Borrow Ram Power"
    assert created.created_at is not None
    assert created.updated_at is not None
    
def test_get_job_found_and_not_found(job_db: JobDatabase):
    user_id = uuid4()
    job_id = uuid4()
    created = job_db.create(make_job(user_id, job_id))
    
    assert created.user_id == user_id
    assert created.job_id == job_id
    with pytest.raises(JobNotFoundException):
        job_db.get("000000000000000000000000")
    assert created is not None
    
def test_list_jobs_filter_and_pagination(job_db: JobDatabase):
    user_a = uuid4()
    user_b = uuid4()
    
    job_db.create(make_job(user_a, uuid4()))
    job_db.create(make_job(user_a, uuid4()))
    job_db.create(make_job(user_b, uuid4()))
    
    all_jobs = job_db.list_all(user_id=None)
    assert len(all_jobs) == 3
    
    a_jobs = job_db.list_all(user_id=user_a)
    assert len(a_jobs) == 2
    assert a_jobs[0].created_at is not None and a_jobs[1].created_at is not None
    assert a_jobs[0].created_at >= a_jobs[1].created_at
    
    paged = job_db.list_all(user_id=None, skip=1, limit=1)
    assert len(paged) == 1
    
def test_update_job_success(job_db: JobDatabase):
    user_id = uuid4()
    job_id = uuid4()
    
    created = job_db.create(make_job(user_id, job_id))
    
    updated_model = Job(
        user_id=created.user_id, 
        job_id=created.job_id,
        job_name="Borrow RAM Power - Afternoon",
        job_description="Second run",
        repo_url=HttpUrl("https://github.com/updated/repo.git"),
        created_at=None,
        updated_at=None
    )
    updated = job_db.update(str(created.job_id), updated_model)
    assert updated is not None
    assert updated.job_id == created.job_id
    assert updated.job_name == "Borrow RAM Power - Afternoon"
    assert updated.job_description == "Second run"
    
def test_update_job_invalid_repo_url_raises(job_db: JobDatabase):
    user_id = uuid4()
    job_id = uuid4()
    created = job_db.create(make_job(user_id, job_id))
    
    with pytest.raises(ValidationError):
        bad_model = Job(
            user_id=created.user_id,
            job_id=created.job_id,
            job_name=created.job_name,
            job_description=created.job_description,
            repo_url="https://your-url.com/not-repo",  # invalid repo_url # type: ignore
            created_at=created.created_at,
            updated_at=created.updated_at
        )
        
        job_db.update(str(created.job_id), bad_model)
        
def test_update_job_disallowed_field_raise(job_db: JobDatabase):
    user_id = uuid4()
    job_id = uuid4()
    created = job_db.create(make_job(user_id, job_id))
    
    with pytest.raises(ValueError):
        bad_model = Job(
            user_id=uuid4(), # Changed to a new user_id
            job_id=uuid4(), # Changed to a new job_id
            job_name=created.job_name,
            job_description=created.job_description,
            repo_url=created.repo_url,
            created_at=created.created_at,
            updated_at=created.updated_at
        )
        job_db.update(str(created.job_id), bad_model)
        
def test_update_job_not_found_raises_exception(job_db: JobDatabase):
    missing_id = str(uuid4())
    dummy_job = Job(
        user_id=uuid4(),
        job_id=uuid4(), 
        job_name="New Name",
        job_description="New Description",
        repo_url=HttpUrl("https://github.com/test/repo.git"),
        created_at=None,
        updated_at=None
    )
    
    with pytest.raises(JobNotFoundException):
        job_db.update(missing_id, dummy_job)
    
def test_update_job_failure_raises_runtimeerror(job_db: JobDatabase, monkeypatch: MonkeyPatch):
    user_id = uuid4()
    job_id = uuid4()
    created = job_db.create(make_job(user_id, job_id))
    
    def boom(*args: Any, **kwargs: Any):
        raise PyMongoError("Kaboom!")
    
    monkeypatch.setattr(job_db.collection, "update_one", boom) # type: ignore
    
    updated_job = Job(
        user_id=created.user_id,
        job_id=created.job_id,
        job_name="Updated Name",
        job_description=created.job_description,
        repo_url=created.repo_url,
        created_at=None,
        updated_at=None
    )
    
    with pytest.raises(RuntimeError):
        job_db.update(str(created.job_id), updated_job)
    
def test_create_job_db_failure_raises_runtimeerror(job_db: JobDatabase, monkeypatch: MonkeyPatch):
    def boom(*args: Any, **kwargs: Any):
        raise PyMongoError("Kaboom!")
    
    monkeypatch.setattr(job_db.collection, "insert_one", boom) # type: ignore
    
    with pytest.raises(RuntimeError):
        job_db.create(make_job(uuid4(), uuid4()))
        
def test_delete_job_success_and_idempotent(job_db: JobDatabase):
    user_id = uuid4()
    job_id = uuid4()
    created = job_db.create(make_job(user_id, job_id))
    
    ok = job_db.delete(created.job_id)
    assert ok is True
    
    with pytest.raises(JobNotFoundException):
        job_db.delete(created.job_id)
    
def test_delete_job_invalid_object_id_raises(job_db: JobDatabase):
    with pytest.raises(ValueError):
        job_db.delete("invalid-object-id")