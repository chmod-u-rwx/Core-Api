from threading import Lock
from fastapi import APIRouter, HTTPException

from src.core_api.models.master_node import MasterNode
from src.core_api.db.master_node_db import MasterNodeDatabase

router = APIRouter(prefix="/master-node", tags=["MasterNode"])
_rr_lock = Lock()
_rr_index = [0]

@router.post("/register", response_model=MasterNode)
def register_master_node(node: MasterNode):
    existing = MasterNodeDatabase().collection.find_one({"master_id": str(node.master_id)})
    
    if existing:
        raise HTTPException(status_code=409, detail="Master node already registered")
    
    MasterNodeDatabase().collection.insert_one(node.model_dump(mode="json", by_alias=True))
    return node

@router.get("/discover", response_model=MasterNode)
def discover_master_node():
    docs = list(MasterNodeDatabase().collection.find())
    if not docs:
        raise HTTPException(status_code=404, detail="No master node available")
    
    docs.sort(key=lambda d: d.get("master_id"))
    with _rr_lock:
        idx = _rr_index[0] % len(docs)
        _rr_index[0] += 1
        
    doc=docs[idx]
    doc.pop("_id", None)
    return MasterNode(**doc)