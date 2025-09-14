from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.core_api.routes.cost_route import router

app = FastAPI()
app.include_router(router)

def test_get_resource_cost():
    client = TestClient(app)
    response = client.get("/cost/")
    assert response.status_code == 200
    data = response.json()
    assert data["cpu_core_cost_per_second"] == 0.03
    assert data["ram_gb_cost_per_second"] == 0.05