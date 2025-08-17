from uuid import uuid4
import pytest
import mongomock
from typing import Any
from fastapi.testclient import TestClient
from mongomock import MongoClient
from unittest.mock import patch
from src.core_api.models.master_node import MasterNode
from src.core_api.app import app

@pytest.fixture
def client():
    with patch("src.core_api.db.master_node_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        yield TestClient(app)

def test_register_master_node_success(client: Any):
    node = MasterNode(
        master_id=uuid4(),
        master_address="192.168.1.100"
    ).model_dump(mode="json")
    response = client.post("/master-node/register", json=node)
    
    assert response.status_code == 200
    assert response.json()["master_id"] == node["master_id"]
    assert response.json()["master_address"] == node["master_address"]
    
def test_register_master_node_duplicate(client: Any):
    node = MasterNode(
        master_id=uuid4(),
        master_address="192.168.1.100"
    ).model_dump(mode="json")
    resp_one = client.post("/master-node/register", json=node)
    assert resp_one.status_code == 200
    resp_two = client.post("/master-node/register", json=node)
    assert resp_two.status_code == 409
    assert "already exists" in resp_two.json()["detail"]
    
def test_register_invalid_master_address(client: Any):
    node = {
        "master_id": str(uuid4()),
        "master_address": "Not a valid address"
    }
    
    response = client.post("/master-node/register", json=node)
    assert response.status_code == 422

def test_discover_master_node_success(client: Any):
    nodes = [
        MasterNode(master_id=uuid4(), master_address="10.0.0.1").model_dump(mode="json"),
        MasterNode(master_id=uuid4(), master_address="10.0.0.2").model_dump(mode="json"),
        MasterNode(master_id=uuid4(), master_address="10.0.0.3").model_dump(mode="json"),
    ]

    for node in nodes:
        client.post("/master-node/register", json=node)

    sorted_nodes = sorted(nodes, key=lambda n: n["master_id"])
    for i in range(2 * len(nodes)):
        response = client.get("/master-node/discover")
        assert response.status_code == 200
        expected = sorted_nodes[i % len(nodes)]
        assert response.json()["master_id"] == expected["master_id"]

def test_discover_master_node_empty(client: Any):
    response = client.get("/master-node/discover")
    assert response.status_code == 404
    assert response.json()["detail"] == "No master node available"

def test_discover_master_node_single(client: Any):
    node = MasterNode(
        master_id=uuid4(),
        master_address="10.0.0.42"
    ).model_dump(mode="json")
    
    client.post("/master-node/register", json=node)
    
    for _ in range(3):
        response = client.get("/master-node/discover")
        assert response.status_code == 200
        assert response.json()["master_address"] == node["master_address"]

def test_register_missing_fields(client: Any):
    response = client.post("/master-node/register", json={"master_address": "10.0.0.1"})
    assert response.status_code == 422
    
    response = client.post("/master-node/register", json={"master_id": str(uuid4())})
    assert response.status_code == 422

def test_register_invalid_uuid(client: Any):
    node = {
        "master_id": "not-a-uuid",
        "master_address": "10.0.0.1"
    }
    
    response = client.post("/master-node/register", json=node)
    assert response.status_code == 422