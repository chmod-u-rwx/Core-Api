from datetime import datetime
from typing import Optional
from uuid import UUID
from ..db.worker_node_db import WorkerNodeDatabase, WorkerNodeResourceDatabase
from ..models.worker_node import WorkerNode, WorkerNodeResources, WorkerNodeUpdates

class WorkerNodeService:
    def __init__(self, node_db: WorkerNodeDatabase):
        self.db = node_db

    def update_node(self, node_id: UUID, node_updates: WorkerNodeUpdates) -> WorkerNode:
        return self.db.update_node(node_id, node_updates)

class WorkerNodeResourceService:
    def __init__(self, node_db: WorkerNodeResourceDatabase):
        self.db = node_db
    
    def insert_resource_report(self, resource: WorkerNodeResources) -> WorkerNodeResources:
        return self.db.insert(resource)

    def get_resource_reports(self, worker_id: Optional[UUID] = None, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> list[WorkerNodeResources]:
        return self.db.list_resources(worker_id, start_time, end_time)

    