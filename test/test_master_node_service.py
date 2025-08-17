from uuid import uuid4
import mongomock
import pytest
from typing import Any
from unittest.mock import patch
from mongomock import MongoClient
from src.core_api.db.master_node_db import MasterNodeNotFoundException
from src.core_api.models.master_node import MasterNode
from src.core_api.services.master_node_service import MasterNodeService

@pytest.fixture
def service():
    with patch("src.core_api.db.master_node_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        yield MasterNodeService()

def create_node(address: str = "192.168.1.100"):
    return MasterNode(master_id=uuid4(), master_address=address)

def test_register_master_node_success(service: MasterNodeService):
    node = create_node()
    registered = service.register(node)
    assert registered.master_id == node.master_id
    assert registered.master_address == node.master_address

def test_register_duplicate_master_node(service: MasterNodeService):
    node = create_node()
    service.register(node)
    with pytest.raises(ValueError):
        service.register(node)

def test_discover_round_robin(service: MasterNodeService):
    nodes = [
        create_node("10.0.0.1"),
        create_node("10.0.0.2"),
        create_node("10.0.0.3"),
    ]
    
    for node in nodes:
        service.register(node)
    
    sorted_nodes = sorted(nodes, key=lambda n: str(n.master_id))
    
    for i in range(2 * len(nodes)):
        discovered = service.discover()
        expected = sorted_nodes[i % len(nodes)]
        assert discovered.master_id == expected.master_id

def test_discover_no_nodes(service: MasterNodeService):
    with pytest.raises(MasterNodeNotFoundException):
        service.discover()

def test_register_and_discover_single_node(service: MasterNodeService):
    node = create_node()
    service.register(node)
    for _ in range(3):
        discovered = service.discover()
        assert discovered.master_id == node.master_id

def test_thread_safety_of_round_robin(service: MasterNodeService):
    nodes = [create_node(f"10.0.0.{i}") for i in range(1, 6)]
    for node in nodes:
        service.register(node)
    result = [service.discover().master_id for _ in range(10)]
    assert set(result) == set(n.master_id for n in nodes)

def test_unregister_existing_node(service: MasterNodeService):
    node = create_node()
    service.register(node)
    assert service.unregister(node.master_id) is True
    with pytest.raises(MasterNodeNotFoundException):
        service.discover()

def test_unregister_nonexistent_node(service: MasterNodeService):
    fake_id = uuid4()
    with pytest.raises(MasterNodeNotFoundException):
        service.unregister(fake_id)