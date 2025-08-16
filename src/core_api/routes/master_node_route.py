from fastapi import APIRouter, HTTPException

from src.core_api.models.master_node import MasterNode
from src.core_api.db.master_node_db import MasterNodeDatabase

router = APIRouter(prefix="/master-node", tags=["MasterNode"])

@router.post("/register", response_model=MasterNode)
def register_master_node(node: MasterNode):
    existing = MasterNodeDatabase().collection.find_one({"master_id": str(node.master_id)})
    
    if existing:
        raise HTTPException(status_code=409, detail="Master node already registered")
    
    MasterNodeDatabase().collection.insert_one(node.model_dump(mode="json", by_alias=True))
    return node

@router.get("/discover", response_model=MasterNode)
def discover_master_node():
    doc = MasterNodeDatabase().collection.find_one()
    
    if not doc:
        raise HTTPException(status_code=404, detail="No master node available")
    
    doc.pop("_id", None)
    return MasterNode(**doc)