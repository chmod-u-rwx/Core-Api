from typing import Optional
from ..db.node_database import NodeDatabase
from ..models.node import Node


class NodeService:
    def __init__(self, node_db: NodeDatabase):
        self.node_db = node_db

    def set_available_job_slots(self, node_id: str, new_slots: int) -> Optional[Node]:

        if new_slots < 0:
            raise ValueError("Job slots cannot be negative.")

        return self.node_db.update_node(node_id, {"job_slots": new_slots})
