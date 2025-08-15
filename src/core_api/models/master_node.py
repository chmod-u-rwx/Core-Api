import re
from pydantic import UUID4, BaseModel, Field, field_validator
import ipaddress

# Each label: no start/end hyphen, length 1–63
label = r"(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
# Domain: at least two labels, last is alpha-only TLD (≥2 chars)
domain_pattern = re.compile(rf"^{label}(\.{label})+\.[A-Za-z]{{2,}}$")

class MasterNode(BaseModel):
    master_id: UUID4 = Field(...)
    master_address: str = Field(...)
    
    @field_validator('master_address')
    @classmethod
    def valid_ip_address(cls, v: str):
        v = v.strip()
        
        if not v:
            raise ValueError("master_address cannot be empty")
            
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            ...
        
        if domain_pattern.match(v):
            return v
        
        raise ValueError("master_address should contain a valid IP Address or domain name")