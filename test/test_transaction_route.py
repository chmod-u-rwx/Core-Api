from typing import Any, List, Dict
from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient
from mongomock import MongoClient
from unittest.mock import patch
from src.core_api.models.transaction import Transaction, TransactionStatus
from src.core_api.app import app
import pytest
import mongomock


@pytest.fixture
def client():
    with patch("src.core_api.db.transaction_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        yield TestClient(app)


@pytest.fixture
def create_transaction() -> Transaction:
    now = datetime.now(timezone.utc)
    return Transaction(
        transaction_id=uuid4(),
        request_id=uuid4(),
        job_id=uuid4(),
        worker_id=uuid4(),
        timestamp=now,
        cost_ram=0.05,
        cost_cpu=0.1,
        execution_time=2.5,
        total_cost=0.375,
        status=TransactionStatus.PAID,
    )


def test_create_transaction(client: TestClient, create_transaction: Transaction) -> None:
    response = client.post(
        "/transactions/",
        json=create_transaction.model_dump(mode="json")
    )
    assert response.status_code == 200
    data: Dict[str, Any] = response.json()
    assert data["transaction_id"] == str(create_transaction.transaction_id)
    assert data["status"] == TransactionStatus.PAID.value


def test_get_transaction(client: TestClient, create_transaction: Transaction) -> None:
    client.post("/transactions/", json=create_transaction.model_dump(mode="json"))
    response = client.get(f"/transactions/{create_transaction.transaction_id}")
    assert response.status_code == 200
    data: Dict[str, Any] = response.json()
    assert data["transaction_id"] == str(create_transaction.transaction_id)


def test_get_transaction_history(client: TestClient, create_transaction: Transaction) -> None:
    client.post("/transactions/", json=create_transaction.model_dump(mode="json"))
    response = client.get("/transactions/history")
    assert response.status_code == 200
    data: List[Dict[str, Any]] = response.json()
    assert isinstance(data, list)
    assert any(tx["transaction_id"] == str(create_transaction.transaction_id) for tx in data)


def test_get_summary(client: TestClient, create_transaction: Transaction) -> None:
    client.post("/transactions/", json=create_transaction.model_dump(mode="json"))
    response = client.get("/transactions/summary")
    assert response.status_code == 200
    data: Dict[str, Any] = response.json()
    assert "total_expenses" in data
    assert "paid_expenses" in data
    assert "pending_expenses" in data
    assert "earning_rate" in data
    assert "average_earnings" in data
