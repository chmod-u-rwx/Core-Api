
from typing import Any, Optional
import pytest
from mongomock import MongoClient
from uuid import UUID, uuid4
from datetime import datetime
from unittest.mock import patch

from src.core_api.db.worker_node_db import WorkerNodeResourceDatabase, WorkerNodeResources


# Override get_mongo_client to use mongomock
@pytest.fixture(autouse=True)
def use_mongomock():
    def fake_client() -> Any:
        client: MongoClient[Any] = MongoClient()
        return client
    with patch("src.core_api.db.worker_node_db.get_mongo_client", fake_client):
        yield


@pytest.fixture
def db():
    return WorkerNodeResourceDatabase()


def make_resource(worker_id: Optional[UUID]=None, timestamp: Optional[datetime]=None):
    return WorkerNodeResources(
        worker_id=worker_id or uuid4(),
        timestamp=timestamp or datetime.now(), 
        job_slots=4,
        cpu_percentage=55.5,
        memory_usage=2048,
        memory_free=8192,
        cache_free=10240,
        cache_used=5120,
    )

def test_check_indexes(db: WorkerNodeResourceDatabase):
    indexes = db.collection.index_information()
    assert "worker_id_1" in indexes
    assert "timestamp_1" in indexes


def test_insert_success(db: WorkerNodeResourceDatabase):
    resource = make_resource()
    result = db.insert(resource)
    assert result == resource
    assert db.collection.count_documents({}) == 1


def test_list_resources_no_filters(db: WorkerNodeResourceDatabase):
    worker_id = uuid4()
    db.insert(make_resource(worker_id))
    db.insert(make_resource(worker_id))

    results = db.list_resources()
    assert len(results) == 2
    assert all(isinstance(r, WorkerNodeResources) for r in results)


def test_list_resources_with_filters(db: WorkerNodeResourceDatabase):
    worker_id = uuid4()
    start_time = datetime(2023, 1, 1, 0, 0)
    mid_time = datetime(2023, 1, 1, 12, 0)
    end_time = datetime(2023, 1, 2, 0, 0)

    r1 = make_resource(worker_id, start_time)
    r2 = make_resource(worker_id, mid_time)
    r3 = make_resource(worker_id, end_time)

    db.insert(r1)
    db.insert(r2)
    db.insert(r3)

    results = db.list_resources(worker_id=worker_id,
                                start_time=start_time,
                                end_time=end_time)

    assert {r.timestamp for r in results} == {start_time, mid_time, end_time}