from typing import Optional
from pydantic import ValidationError
from ..db.node_database import NodeDatabase
from ..models.node import Node

class NodeService:
    def __init__(self, node_db: NodeDatabase):
        self.node_db = node_db
    def set_job_slots(self, node_id: str, slots: int) -> Optional[Node]:
        try:
            Node(node_id=node_id, job_slots=slots)
            if slots < 0:
                raise ValueError("Job slots cannot be empty")
            return self.node_db.update_node(node_id, {"job_slots": slots})
        except ValidationError as e:
            raise ValueError(f"Invalid job slots value: {str(e)}")