from uuid import uuid4
import mongomock
import pytest
from pytest import MonkeyPatch
from typing import Any
from mongomock import MongoClient
from pymongo.errors import PyMongoError
from unittest.mock import patch
from src.core_api.models.master_node import MasterNode, UpdateMasterNode
from src.core_api.db.master_node_db import MasterNodeDatabase, MasterNodeNotFoundException

@pytest.fixture
def master_node_db():
    with patch("src.core_api.db.master_node_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        db = MasterNodeDatabase()
        yield db

# --- Master Node Database Test Cases ---
def test_collection_and_index(master_node_db: MasterNodeDatabase):
    assert master_node_db.collection.name == "master_node"
    
    indexes = master_node_db.collection.index_information()
    assert "idx_master_id" in indexes
    
def test_index_creation_error():
    with patch("src.core_api.db.master_node_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        with patch("mongomock.collection.Collection.create_index", side_effect=PyMongoError("Index error")):
            with pytest.raises(RuntimeError) as e:
                MasterNodeDatabase()
            assert "Index creation failed" in str(e.value)

def test_db_init_error():
    with patch("src.core_api.db.master_node_db.get_mongo_client", side_effect=PyMongoError("Connection error")):
        with pytest.raises(RuntimeError) as e:
            MasterNodeDatabase()
        assert "Database initialization failed" in str(e.value)

# --- Master Node CRUD Operations Test Cases ---
def create_sample_node():
    return MasterNode(master_id=uuid4(), master_address="192.168.1.100")

def test_create_and_get_master_node(master_node_db: MasterNodeDatabase):
    node = create_sample_node()
    created = master_node_db.create(node)
    assert created.master_id == node.master_id
    assert created.master_address == node.master_address
    
    fetched = master_node_db.get(node.master_id)
    assert fetched.master_id == node.master_id
    assert fetched.master_address == node.master_address

def test_craete_no_inserted_id(monkeypatch: MonkeyPatch, master_node_db: MasterNodeDatabase):
    node = MasterNode(master_id=uuid4(), master_address="10.0.0.2")
    class FakeResult:
        inserted_id = None
        monkeypatch.setattr(master_node_db.collection, "insert_one", lambda *a, **kw: FakeResult()) # type: ignore
    with pytest.raises(RuntimeError, match="No inserted_id returned"):
        master_node_db.create(node)

def test_get_nonexistent_master_node(master_node_db: MasterNodeDatabase):
    with pytest.raises(MasterNodeNotFoundException):
        master_node_db.get(uuid4())

def test_create_pymongo_error(monkeypatch: MonkeyPatch, master_node_db: MasterNodeDatabase):
    node = MasterNode(master_id=uuid4(), master_address="10.0.0.3")
    def boom(*a: Any, **kw: Any):
        from pymongo.errors import PyMongoError
        raise PyMongoError("Kaboom!")
    monkeypatch.setattr(master_node_db.collection, "insert_one", boom)
    with pytest.raises(RuntimeError, match="Failed to create master node: Kaboom!"):
        master_node_db.create(node)

def test_list_all_master_nodes(master_node_db: MasterNodeDatabase):
    node_one = create_sample_node()
    node_two = MasterNode(master_id=uuid4(), master_address="10.0.0.2")
    master_node_db.create(node_one)
    master_node_db.create(node_two)
    
    all_nodes = master_node_db.list_all()
    addresses = {n.master_address for n in all_nodes}
    
    assert node_one.master_address in addresses
    assert node_two.master_address in addresses
    assert len(all_nodes) == 2

def test_update_master_node(master_node_db: MasterNodeDatabase):
    node = create_sample_node()
    master_node_db.create(node)
    update = UpdateMasterNode(master_address="10.10.10.10")
    updated = master_node_db.update(node.master_id, update)
    assert updated.master_address == "10.10.10.10"

def test_update_nonexistent_master_node(master_node_db: MasterNodeDatabase):
    update = UpdateMasterNode(master_address="10.10.10.10")
    with pytest.raises(MasterNodeNotFoundException):
        master_node_db.update(uuid4(), update)

def test_update_no_fields(master_node_db: MasterNodeDatabase):
    node = create_sample_node()
    master_node_db.create(node)
    update=UpdateMasterNode()
    with pytest.raises(ValueError):
        master_node_db.update(node.master_id, update)

def test_delete_master_node(master_node_db: MasterNodeDatabase):
    node = create_sample_node()
    master_node_db.create(node)
    deleted = master_node_db.delete(node.master_id)
    assert deleted
    with pytest.raises(MasterNodeNotFoundException):
        master_node_db.get(node.master_id)

def test_delete_nonexistent_master_node(master_node_db: MasterNodeDatabase):
    with pytest.raises(MasterNodeNotFoundException):
        master_node_db.delete(uuid4())