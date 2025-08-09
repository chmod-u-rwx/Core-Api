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

def test_create_job_success():
    response = client.post("/jobs/", json=sample_job_format)
    assert response.status_code == 200
    assert response.json()["message"] == "Job created"

def test_create_job_fail_missing_field():
    invalid_job = sample_job_format.copy()
    del invalid_job["job_name"]
    response = client.post("/jobs/", json=invalid_job)
    assert response.status_code == 422  # Validation error

# -------------------------------
# UPDATE JOB TESTS
# -------------------------------
def test_update_job_success():
    # Create first to update
    create_res = client.post("/jobs/", json=sample_job)
    job_id = create_res.json()["job"]["id"]

    updated_job = sample_job.copy()
    updated_job["job_name"] = "Updated Name"
    response = client.put(f"/jobs/{job_id}", json=updated_job)
    assert response.status_code == 200
    assert response.json()["job"]["job_name"] == "Updated Name"

def test_update_job_fail_not_found():
    job_id = str(uuid4())  # Non-existent
    updated_job = sample_job.copy()
    updated_job["job_name"] = "Updated Name"
    response = client.put(f"/jobs/{job_id}", json=updated_job)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

# -------------------------------
# READ JOB TESTS
# -------------------------------
def test_read_job_success():
    create_res = client.post("/jobs/", json=sample_job)
    job_id = create_res.json()["job"]["id"]

    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job"]["id"] == job_id

def test_read_job_fail_not_found():
    job_id = str(uuid4())  # Non-existent
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

# -------------------------------
# DELETE JOB TESTS
# -------------------------------
def test_delete_job_success():
    create_res = client.post("/jobs/", json=sample_job)
    job_id = create_res.json()["job"]["id"]

    response = client.delete(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Job deleted"

def test_delete_job_fail_not_found():
    job_id = str(uuid4())  # Non-existent
    response = client.delete(f"/jobs/{job_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()