from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from src.core_api.db.worker_node_db import WorkerNodeDatabase, WorkerNodeResourceDatabase
from src.core_api.models.worker_node import WorkerNodeResources, WorkerNodeUpdates, WorkerNode
from src.core_api.services.worker_node_service import WorkerNodeResourceService, WorkerNodeService
from src.core_api.db.worker_node_db import InvalidUpdate

router = APIRouter(prefix="/worker-node",tags= ["Nodes"] )

@router.post("/update", response_model=WorkerNode)
def update_node(node_id: UUID, updates: WorkerNodeUpdates):
    try:
        return WorkerNodeService(WorkerNodeDatabase()).update_node(node_id, updates)
    except InvalidUpdate:
        raise HTTPException(status_code=409, detail="Supply atleast one update in body")
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Node with id {node_id} does not exist")

@router.post("/resource-reports", response_model=WorkerNodeResources)
def report_resources(resource: WorkerNodeResources):
    try:
        return WorkerNodeResourceService(WorkerNodeResourceDatabase()).insert_resource_report(resource)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resource-reports", response_model=list[WorkerNodeResources])
def get_resource_reports(worker_id: Optional[UUID] = Query(None), 
                         start_time: Optional[datetime] = Query(None),
                         end_time: Optional[datetime] = Query(None)):
    try:
        return WorkerNodeResourceService(WorkerNodeResourceDatabase()).get_resource_reports(worker_id, start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


