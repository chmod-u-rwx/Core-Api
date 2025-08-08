import pytest
from uuid import uuid4
from pydantic import ValidationError, HttpUrl
from src.core_api.models.job import Job

def test_job_model_valid():
    job = Job(
        user_id=uuid4(),
        job_name="Pahiram Ram",
        job_description="Pahiram lang, damot",
        repo_url="https://github.com/example/repo.git",
    )
    
    assert job.job_name == "Pahiram Ram"
    assert job.repo_url == HttpUrl("https://github.com/example/repo.git")
    
def test_job_model_not_github_url():
    with pytest.raises(ValidationError):
        Job(
            user_id=uuid4(),
            job_name="test job.",
            job_description="test job ngani",
            repo_url="https://facebook.com/"
        )