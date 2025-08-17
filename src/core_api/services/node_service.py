from uuid import UUID
from ..db.node_database import NodeDatabase
from ..models.node_model import Node, NodeUpdates

class NodeService:
    def __init__(self, node_db: NodeDatabase):
        self.db = node_db

    def set_job_slots(self, node_id: UUID, job_slots: int) -> Node:
        if job_slots < 0:
            raise ValueError("job_slots must be >= 0")
        
        updates = NodeUpdates(job_slots=job_slots)
        return self.db.update_node(node_id, updates)
