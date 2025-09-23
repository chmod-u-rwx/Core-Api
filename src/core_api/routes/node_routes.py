from uuid import UUID
from fastapi import APIRouter, HTTPException
from src.core_api.db.worker_node_db import NodeDatabase
from src.core_api.models.worker_node import WorkerNodeUpdates, WorkerNode
from src.core_api.services.node_service import NodeService
from src.core_api.db.worker_node_db import InvalidUpdate

router = APIRouter(prefix="/worker-node",tags= ["Nodes"] )

@router.post("/update", response_model=WorkerNode)
def update_node(node_id: UUID, updates: WorkerNodeUpdates):
    try:
        return NodeService(NodeDatabase()).update_node(node_id, updates)
    except InvalidUpdate:
        raise HTTPException(status_code=409, detail="Supply atleast one update in body")
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Node with id {node_id} does not exist")
