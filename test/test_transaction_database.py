from datetime import datetime, timezone, timedelta
from uuid import uuid4
import pytest
from typing import Any
from unittest.mock import patch
from mongomock import MongoClient

from src.core_api.models.transaction import Transaction
from src.core_api.db.transaction_db import (TransactionDatabase,TransactionNotFoundException,)


@pytest.fixture
def transaction_db():
    with patch("src.core_api.db.transaction_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = MongoClient()
        mock_get_client.return_value = mock_client

        db = TransactionDatabase()
        yield db


@pytest.fixture
def make_transaction() -> Transaction:
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
    )


def test_create_and_get(transaction_db: TransactionDatabase, make_transaction: Transaction):
    created = transaction_db.create(make_transaction)
    assert created.transaction_id == make_transaction.transaction_id
    assert created.total_cost == make_transaction.total_cost

    fetched = transaction_db.get(make_transaction.transaction_id)
    assert fetched.job_id == make_transaction.job_id
    assert fetched.execution_time == make_transaction.execution_time


def test_list_transactions_filters(transaction_db: TransactionDatabase, make_transaction: Transaction):
    transaction_db.create(make_transaction)

    results = transaction_db.list_transactions(job_id=make_transaction.job_id)
    assert len(results) == 1

    results = transaction_db.list_transactions(worker_id=make_transaction.worker_id)
    assert len(results) == 1

    start = make_transaction.timestamp - timedelta(hours=1)
    end = make_transaction.timestamp + timedelta(hours=1)
    results = transaction_db.list_transactions(start_time=start, end_time=end)
    assert len(results) == 1

    start = datetime.now(timezone.utc) + timedelta(days=1)
    results = transaction_db.list_transactions(start_time=start)
    assert len(results) == 0


def test_delete(transaction_db: TransactionDatabase, make_transaction: Transaction):
    transaction_db.create(make_transaction)
    transaction_db.delete(make_transaction.transaction_id)

    with pytest.raises(TransactionNotFoundException):
        transaction_db.get(make_transaction.transaction_id)


def test_get_not_found(transaction_db: TransactionDatabase):
    with pytest.raises(TransactionNotFoundException):
        transaction_db.get(uuid4())


def test_delete_not_found(transaction_db: TransactionDatabase):
    with pytest.raises(TransactionNotFoundException):
        transaction_db.delete(uuid4())
