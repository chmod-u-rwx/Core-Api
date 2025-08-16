from uuid import uuid1, uuid4
from pydantic import ValidationError
import pytest
from src.core_api.models.master_node import MasterNode

def test_valid_master_node_model():
    node = MasterNode(
        master_id=uuid4(),
        master_address="192.168.1.10"
    )
    
    assert node.master_id
    assert node.master_address == "192.168.1.10"
    
def test_valid_ipv6():
    node = MasterNode(
        master_id=uuid4(),
        master_address="2001:db8::1"
    )
    
    assert node.master_address == "2001:db8::1"
    
def test_valid_domain():
    node = MasterNode(
        master_id=uuid4(),
        master_address="test.com"
    )
    
    assert node.master_address == "test.com"
    
def test_valid_subdomain():
    node = MasterNode(
        master_id=uuid4(),
        master_address="sub.domain-example.com"
    )
    
    assert node.master_address == "sub.domain-example.com"
    
@pytest.mark.parametrize(
    "bad_address",
    [
        "256.256.256.256",
        "2001:db8::g",    
        "not a domain",   
        "-bad.com",       
        "bad-.com",       
        ".bad.com",       
        "bad.com.",       
        "",               
        " ",              
    ],
)
def test_invalid_master_address_raises(bad_address: str):
    with pytest.raises(ValidationError) as e:
        MasterNode(master_id=uuid4(), master_address=bad_address)
    assert "master_address" in str(e.value)
    
def test_invalid_uuid_string_for_master_id():
    with pytest.raises(ValidationError) as ei:
        MasterNode(master_id="not-a-uuid", master_address="10.0.0.1") # type: ignore
    assert "master_id" in str(ei.value)
    
def test_uuid1_is_rejected_uuid4_required():
    with pytest.raises(ValidationError) as ei:
        MasterNode(master_id=str(uuid1()), master_address="10.0.0.1") # type: ignore
    
    assert "master_id" in str(ei.value)
    
def test_missing_fields_raise():
    with pytest.raises(ValidationError):
        MasterNode(master_id=uuid4()) # type: ignore
        
    with pytest.raises(ValidationError):
        MasterNode(master_address="192.168.1.1") # type: ignore
        
def test_model_dump_roundtrip_preserves_values():
    m_id = uuid4()
    addr = "203.0.113.5"
    node = MasterNode(master_id=m_id, master_address=addr)
    dumped = node.model_dump()
    assert dumped["master_id"] == m_id
    assert dumped["master_address"] == addr
    
def test_extra_fields_are_ignored_by_default():
    node = MasterNode(master_id=uuid4(), master_address="10.0.0.1", extra_field="ignored")
    
    # Default BaseModel (Pydantic v2) ignores extras unless configured otherwise
    with pytest.raises(AttributeError):
        _ = node.extra_field # type: ignore