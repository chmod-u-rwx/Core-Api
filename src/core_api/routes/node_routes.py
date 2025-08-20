from uuid import UUID
from fastapi import APIRouter, HTTPException
from src.core_api.db.node_database import NodeDatabase
from src.core_api.models.node_model import Node
from src.core_api.services.node_service import NodeService

router = APIRouter(prefix="/nodes",tags= ["Nodes"] )

@router.post("/set_job_slots", response_model=Node)
def set_job_slots(node_id: UUID, job_slots: int):
    try:
        return NodeService(NodeDatabase()).set_job_slots(node_id, job_slots)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))