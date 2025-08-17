from fastapi import APIRouter, HTTPException
from src.core_api.db.master_node_db import MasterNodeNotFoundException
from src.core_api.models.master_node import MasterNode
from src.core_api.services.master_node_service import MasterNodeService

router = APIRouter(prefix="/master-node", tags=["MasterNode"])

@router.post("/register", response_model=MasterNode)
def register_master_node(node: MasterNode):
    try:
        return MasterNodeService().register(node)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discover", response_model=MasterNode)
def discover_master_node():
    try:
        return MasterNodeService().discover()
    except MasterNodeNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))