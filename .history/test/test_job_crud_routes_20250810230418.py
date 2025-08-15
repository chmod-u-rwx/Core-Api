# /test/test_jobs.py

from fastapi.testclient import TestClient
from src.core_api.models.job import Job
from main import app
from uuid import uuid4

client = TestClient(app)

sample_job_format = Job{
    "userid": str(uuid4()),
    "job_name": "Chosen Job",
    "job_description": "Definition of the job reqs",
    "github_url": "https://github.com/example/repo",
    "version": "v1.1.1"
}


# CREATE JOB
def test_create_job_success(): #create the job w/ correct format
    response = client.post("/jobs/", json=sample_job_format.model_dump)
    assert response.status_code == 200
    assert response.json()["message"] == "Job created"

def test_create_job_fail_missing_field(): # create job w/ missing field
    invalid_job = sample_job_format.model_dump()
    invalid_job["job_name"] 
    response = client.post("/jobs/", json=invalid_job)
    assert response.status_code == 422 

def test_create_job_fail_invalid_url(): # create job w/ invalid URL
    invalid_job = sample_job_format.model_dump()
    invalid_job["github_url"] = "not-a-valid-url"
    response = client.post("/jobs/", json=invalid_job)
    assert response.status_code == 422 

# READ JOB
def test_read_job_success():
    job_id = str(uuid4()) 
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id

def test_read_job_fail_invalid_uuid():
    response = client.get("/jobs/invalid-uuid")
    assert response.status_code == 422 

def test_read_job_fail_not_found():
    job_id = str(uuid4())
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code in [404, 200] 
    if response.status_code == 404:
        assert "not found" in response.json()["detail"].lower()

# UPDATE JOB
def test_update_job_success():
    job_id = str(uuid4())
    updated_job = sample_job_format.model_dump()
    updated_job["job_name"] = "Updated Name"
    response = client.put(f"/jobs/{job_id}", json=updated_job)
    assert response.status_code == 200
    assert response.json()["job"]["job_name"] == "Updated Name"

def test_update_job_fail_empty_content():
    job_id = str(uuid4())
    response = client.put(f"/jobs/{job_id}", json={})
    assert response.status_code == 422

def test_update_job_fail_invalid_uuid():
    updated_job = sample_job_format.model_dump()
    response = client.put("/jobs/invalid-uuid", json=updated_job)
    assert response.status_code == 422

#DELETE JOB
def test_delete_job_success():
    job_id = str(uuid4())
    response = client.delete(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id

def test_delete_job_fail_invalid_uuid():
    response = client.delete("/jobs/invalid-uuid")
    assert response.status_code == 422