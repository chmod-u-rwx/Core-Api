from typing import Any
from uuid import uuid4
from fastapi.testclient import TestClient
import pytest
from pytest import MonkeyPatch
from mongomock import MongoClient as MockMongoClient

@pytest.fixture(scope="session")
def shared_mock_client() -> Any:
    return MockMongoClient() # type: ignore

@pytest.fixture(autouse=True)
def patch_mongo(monkeypatch: MonkeyPatch, shared_mock_client: Any):
    def mock_get_mongo_client():
        return shared_mock_client
    
    monkeypatch.setattr("src.core_api.db.job_db.get_mongo_client", mock_get_mongo_client)
    
from main import app
client: Any = TestClient(app)

def create_sample_job():
    return {
        "user_id": str(uuid4()),
        "job_id": str(uuid4()),
        "job_name": "Sample Job",
        "job_description": "Sample Description",
        "repo_url": "https://github.com/example/repo.git"
    }
    
def test_create_job_success():
    job = create_sample_job()
    response = client.post("/job/create", json=job)
    assert response.status_code == 200
    data = response.json()
    assert data["job_name"] == job["job_name"]
    assert data["job_id"] == job["job_id"]
    
def test_create_job_missing_fields():
    job = create_sample_job()
    del job["job_name"]
    response = client.post("/job/create", json=job)
    assert response.status_code == 422
    
def test_create_job_invalid_url():
    job = create_sample_job()
    job["repo_url"] = "not-a-url"
    response = client.post("/job/create", json=job)
    assert response.status_code == 422
    
def test_create_job_invalid_repo_url():
    job = create_sample_job()
    job["repo_url"] = "https://facebook.com/profile"
    response = client.post("/job/create", json=job)
    assert response.status_code == 422
    
def test_get_job_success():
    job = create_sample_job()
    post = client.post("/job/create", json=job)
    job_id = post.json()["job_id"]
    response = client.get(f"/job/get/{job_id}")
    assert response.status_code == 200
    
def test_get_job_not_found():
    fake_id=str(uuid4())
    response = client.get(f"/job/get/{fake_id}")
    assert response.status_code == 404
    
def test_list_jobs_empty():
    response = client.get("/job/list")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
def test_list_jobs_pagination():
    for _ in range(5):
        client.post("/job/create", json=create_sample_job())
    response = client.get("/job/list?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
def test_list_jobs_user_filter():
    job = create_sample_job()
    client.post("/job/create", json=job)
    user_id = job["user_id"]
    response = client.get(f"/job/list?user_id={user_id}")
    for item in response.json():
        assert item["user_id"] == user_id
    
def test_update_job_success():
    job = create_sample_job()
    post = client.post("/job/create", json=job)
    job_id = post.json()["job_id"]
    update = {"job_name": "Updated Name Test"}
    response = client.put(f"/job/update/{job_id}", json=update)
    assert response.status_code == 200
    assert response.json()["job_name"] == "Updated Name Test"
    
def test_update_job_not_found():
    fake_id = str(uuid4())
    update = {"job_name": "Updated Name Again"}
    response = client.put(f"/job/update/{fake_id}", json=update)
    assert response.status_code == 404
    
def test_update_job_no_fields():
    job = create_sample_job()
    post = client.post("/job/create", json=job)
    job_id = post.json()["job_id"]
    update = {}
    response = client.put(f"/job/update/{job_id}", json=update)
    assert response.status_code == 422
    
def test_delete_job_success():
    job = create_sample_job()
    post = client.post("/job/create", json=job)
    job_id = post.json()["job_id"]
    response = client.delete(f"/job/delete/{job_id}")
    assert response.status_code == 200
    
def test_delete_job_not_found():
    fake_id = str(uuid4())
    response = client.delete(f"/job/delete/{fake_id}")
    assert response.status_code == 404