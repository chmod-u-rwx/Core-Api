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

