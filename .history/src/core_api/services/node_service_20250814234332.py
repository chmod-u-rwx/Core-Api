from typing import Optional
from pydantic import ValidationError
from ..db.node_database import NodeDatabase
from ..models.node import Node

class NodeService:
    def __init__(self, node_db: NodeDatabase):
        self.node_db = node_db

    def set_job_slots(self, node_id: str, slots: int) -> Optional[Node]:
        try:
            if not isinstance(slots, int):
                raise ValueError("Job slots must be an integer")
            if slots < 0:
                raise ValueError("Job slots cannot be negative")

            #validation
            Node(node_id=node_id, job_slots=slots)

            return self.node_db.update_node(node_id, {"job_slots": slots})

        except ValidationError as node_validation_error:
            raise ValueError(f"Invalid job slots value: {str(e)}")
