# /test/test_jobs.py

from fastapi.testclient import TestClient
from main import app
from uuid import uuid4

client = TestClient(app)

sample_job = {
    "userID": str(uuid4()),
    "Job_Name": "Sample Job",
    "Job_Description": "Testing job creation",
    "Github_URL": "https://github.com/example/repo",
    "Version": "v1.0.0"
}

# Success CRUD tests
def test_create_job():
    response = client.post("/jobs/", json=sample_job)
    assert response.status_code == 200
    assert response.json()["message"] == "Job created"

def test_get_job():
    job_id = str(uuid4())
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id

def test_update_job():
    job_id = str(uuid4())
    updated_job = sample_job.copy()
    updated_job["Job_Name"] = "Updated Name"
    response = client.put(f"/jobs/{job_id}", json=updated_job)
    assert response.status_code == 200
    assert response.json()["job"]["Job_Name"] == "Updated Name"

def test_delete_job():
    job_id = str(uuid4())
    response = client.delete(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id

# Fail handling tests

def test_create_job_missing_field():
    job_data = {
        # Missing job_name
        "user_id": str(uuid4()),
        "job_description": "Missing job_name test",
        "github_url": "https://github.com/example/repo",
        "version": "v1.0.0"
    }
    response = client.post("/jobs/", json=job_data)
    assert response.status_code == 422  # Validation error

def test_create_job_invalid_url():
    job_data = sample_job.copy()
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

