import pytest
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import patch
import mongomock
from typing import Any

from src.core_api.models.transaction import Transaction, TransactionStatus
from src.core_api.db.transaction_db import TransactionDatabase
from src.core_api.services.transaction_service import TransactionService


@pytest.fixture
def transaction_service():
    with patch("src.core_api.db.transaction_db.get_mongo_client") as mock_get_client:
        mock_client: mongomock.MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        db = TransactionDatabase()
        yield TransactionService(db)


@pytest.fixture
def create_transactions():
    now = datetime.now(timezone.utc)
    return [
        Transaction(
            transaction_id=uuid4(),
            request_id=uuid4(),
            job_id=uuid4(),
            worker_id=uuid4(),
            timestamp=now,
            cost_ram=0.05,
            cost_cpu=0.1,
            execution_time=5.0,
            total_cost=10.0,
            status=TransactionStatus.PAID,
        ),
        Transaction(
            transaction_id=uuid4(),
            request_id=uuid4(),
            job_id=uuid4(),
            worker_id=uuid4(),
            timestamp=now,
            cost_ram=0.05,
            cost_cpu=0.1,
            execution_time=8.0,
            total_cost=20.0,
            status=TransactionStatus.PENDING,
        ),
        Transaction(
            transaction_id=uuid4(),
            request_id=uuid4(),
            job_id=uuid4(),
            worker_id=uuid4(),
            timestamp=now,
            cost_ram=0.05,
            cost_cpu=0.1,
            execution_time=10.0,
            total_cost=30.0,
            status=TransactionStatus.PAID,
        )
    ]


def test_total_expenses(transaction_service: TransactionService, create_transactions: TransactionDatabase):
    with patch.object(TransactionDatabase, "list_transactions", return_value=create_transactions):
        total = transaction_service.get_total_expenses()
        assert total == 60.0  


def test_paid_expenses(transaction_service: TransactionService, create_transactions: TransactionDatabase):
    with patch.object(TransactionDatabase, "list_transactions", return_value=create_transactions):
        paid = transaction_service.get_paid_expenses()
        assert paid == 40.0  


def test_pending_expenses(transaction_service: TransactionService, create_transactions: TransactionDatabase):
    with patch.object(TransactionDatabase, "list_transactions", return_value=create_transactions):
        pending = transaction_service.get_pending_expenses()
        assert pending == 20.0  


def test_earning_rate(transaction_service: TransactionService, create_transactions: TransactionDatabase):
    with patch.object(TransactionDatabase, "list_transactions", return_value=create_transactions):
        rate = transaction_service.get_earning_rate()
        assert pytest.approx(rate, rel=1e-3) == 40.0 / 23.0 #type:ignore


def test_average_earnings(transaction_service: TransactionService, create_transactions: TransactionDatabase):
    with patch.object(TransactionDatabase, "list_transactions", return_value=create_transactions):
        avg = transaction_service.get_average_earnings()
        assert avg == 20.0


def test_total_earnings_compare(transaction_service: TransactionService, create_transactions: TransactionDatabase):
    with patch.object(TransactionDatabase, "list_transactions", return_value=create_transactions):
        earnings, rate_change = transaction_service.get_total_earnings(compare_start=datetime.now(), compare_end=datetime.now()) #type: ignore
        assert earnings == 40.0
