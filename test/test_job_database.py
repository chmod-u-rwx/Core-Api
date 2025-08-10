from typing import Any
from pydantic import HttpUrl, ValidationError
import pytest
from pytest import MonkeyPatch
from pymongo.errors import PyMongoError
from uuid import uuid4
from mongomock import MongoClient
from src.core_api.db.job_db import JobDatabase
from src.core_api.models.job import Job

@pytest.fixture
def job_db():
    client: MongoClient[Any] = MongoClient()
    db: JobDatabase = JobDatabase(client=client, db_name="test_db", collection_name="jobs_test")
    yield db
    
def make_job(user_id: Any):
    return Job(
        user_id=user_id,
        job_name="Borrow Ram Power",
        job_description="Temporary RAM boost",
        repo_url=HttpUrl("https://github.com/example/repo.git")
    )
    
def test_create_job_returns_job_in_db(job_db: JobDatabase):
    user_id = uuid4()
    created = job_db.create_job(make_job(user_id))
    
    assert created.id
    assert created.user_id == user_id
    assert created.job_name == "Borrow Ram Power"
    assert created.created_at is not None
    assert created.updated_at is not None
    
def test_get_job_found_and_not_found(job_db: JobDatabase):
    user_id = uuid4()
    created = job_db.create_job(make_job(user_id))
    
    fetched = job_db.get_job(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    
    missing = job_db.get_job("000000000000000000000000")
    assert missing is None
    
def test_list_jobs_filter_and_pagination(job_db: JobDatabase):
    user_a = uuid4()
    user_b = uuid4()
    
    job_db.create_job(make_job(user_a))
    job_db.create_job(make_job(user_a))
    job_db.create_job(make_job(user_b))
    
    all_jobs = job_db.list_jobs(user_id=None)
    assert len(all_jobs) == 3
    
    a_jobs = job_db.list_jobs(user_id=user_a)
    assert len(a_jobs) == 2
    assert a_jobs[0].created_at >= a_jobs[1].created_at
    
    paged = job_db.list_jobs(user_id=None, skip=1, limit=1)
    assert len(paged) == 1
    
def test_update_job_success(job_db: JobDatabase):
    user_id = uuid4()
    created = job_db.create_job(make_job(user_id))
    
    updated = job_db.update_job(
        created.id,
        {"job_name": "Borrow RAM Power - Afternoon", "job_description": "Second run"},
    )
    
    assert updated is not None
    assert updated.id == created.id
    assert updated.job_name == "Borrow RAM Power - Afternoon"
    assert updated.job_description == "Second run"
    
def test_update_job_invalid_repo_url_raises(job_db: JobDatabase):
    user_id = uuid4()
    created = job_db.create_job(make_job(user_id))
    
    with pytest.raises(ValidationError):
        job_db.update_job(created.id, {"repo_url": "https://your-url.com/not-repo"})
        
def test_update_job_disallowed_field_raise(job_db: JobDatabase):
    user_id = uuid4()
    created = job_db.create_job(make_job(user_id))
    
    with pytest.raises(ValueError):
        job_db.update_job(created.id, {"user_id": str(uuid4())})
        
def test_update_job_not_found_returns_none(job_db: JobDatabase):
    missing_id = "000000000000000000000000"
    result = job_db.update_job(missing_id, {"job_name": "x"})
    assert result is None
    
def test_update_job_failure_raises_runtimeerror(job_db: JobDatabase, monkeypatch: MonkeyPatch):
    user_id = uuid4()
    created = job_db.create_job(make_job(user_id))
    
    def boom(*args: Any, **kwargs: Any):
        raise PyMongoError("Kaboom!")
    
    monkeypatch.setattr(job_db.collection, "update_one", boom) # type: ignore
    
    with pytest.raises(RuntimeError):
        job_db.update_job(created.id, {"job_name": "x"})
    
def test_create_job_db_failure_raises_runtimeerror(job_db: JobDatabase, monkeypatch: MonkeyPatch):
    def boom(*args: Any, **kwargs: Any):
        raise PyMongoError("Kaboom!")
    
    monkeypatch.setattr(job_db.collection, "insert_one", boom) # type: ignore
    
    with pytest.raises(RuntimeError):
        job_db.create_job(make_job(uuid4()))
        
def test_delete_job_success_and_idempotent(job_db: JobDatabase):
    user_id = uuid4()
    created = job_db.create_job(make_job(user_id))
    
    ok = job_db.delete_job(created.id)
    assert ok is True
    
    assert job_db.get_job(created.id) is None
    assert job_db.delete_job(created.id) is False
    
def test_delete_job_invalid_object_id_raises(job_db: JobDatabase):
    with pytest.raises(ValueError):
        job_db.delete_job("invalid-object-id")