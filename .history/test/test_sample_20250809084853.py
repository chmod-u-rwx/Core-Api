# /test/test_jobs.py

from fastapi.testclient import TestClient
from main import app
from uuid import uuid4

client = TestClient(app)

sample_job_format = {
    "userid": str(uuid4()),
    "job_name": "Chosen Job",
    "job_description": "Definition of the job reqs",
    "github_url": "https://github.com/example/repo",
    "version": "v1.1.1"
}

# Success CRUD tests
def test_create_job():
    response = client.post("/jobs/", json=sample_job_format)
    assert response.status_code == 200
    assert response.json()["message"] == "Job created"

def test_get_job():
    job_id = str(uuid4())
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id

def test_update_job():
    job_id = str(uuid4())
    updated_job = sample_job_format.copy()
    updated_job["job_name"] = "Updated Name"
    response = client.put(f"/jobs/{job_id}", json=updated_job)
    assert response.status_code == 200
    assert response.json()["job"]["job_name"] == "Updated Name"

def test_delete_job():
    job_id = str(uuid4())
    response = client.delete(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id

# Failed CRUD Tests

def test_create_job_missing_field():
    job_data = {
        "user_id": str(uuid4()),
        "job_description": "Missing job information",
        "github_url": "https://github.com/example/repo",
        "version": "v1.1.1"
    }
    response = client.post("/jobs/", json=job_data)
    assert response.status_code == 422 


def test_create_job_invalid_url():
    job_data = sample_job_format.copy()
    job_data["github_url"] = "not-a-valid-url"
    response = client.post("/jobs/", json=job_data)
    assert response.status_code == 422

def test_get_job_invalid_id_format():
    response = client.get("/jobs/not-a-uuid")
    assert response.status_code == 422  # Invalid UUID format

def test_update_job_empty_body():
    job_id = str(uuid4())
    response = client.put(f"/jobs/{job_id}", json={})
    assert response.status_code == 422

def test_delete_job_invalid_id_format():
    response = client.delete("/jobs/123-invalid-uuid")
    assert response.status_code == 422
    
