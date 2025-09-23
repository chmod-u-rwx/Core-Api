from uuid import UUID
from ..db.worker_node_db import NodeDatabase
from ..models.worker_node import WorkerNode, WorkerNodeUpdates

class NodeService:
    def __init__(self, node_db: NodeDatabase):
        self.db = node_db

    def update_node(self, node_id: UUID, node_updates: WorkerNodeUpdates) -> WorkerNode:
        return self.db.update_node(node_id, node_updates)
    