
from src.core_api.app import app  
from src.core_api.models.sample import SampleModel
from fastapi.testclient import TestClient

import pytest

@pytest.fixture()
def test_client() -> TestClient:
    client = TestClient(app)
    return client

def test_get_sample_model(test_client: TestClient):
    response = test_client.get(url="/sample") 
    assert response.status_code == 200
    sample_model = SampleModel(**response.json())

    assert sample_model.name == "Cotton"
