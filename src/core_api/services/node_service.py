from typing import Optional
from uuid import UUID
from pydantic import ValidationError
from ..db.node_database import NodeDatabase
from ..models.node_model import Node

class NodeService:
    def __init__(self, node_db: NodeDatabase):
        self.node_db = node_db

    def set_job_slots(self, node_id: UUID, slots: int) -> Optional[Node]:
        # Validate input
        if not isinstance(slots, int):
            raise ValueError("Job slots must be an integer")
        if slots < 0:
            raise ValueError("Job slots cannot be negative")

        try:
            # Validation via Pydantic model
            Node(node_id=node_id, job_slots=slots)
            updated_node = self.node_db.update_node(node_id, {"job_slots": slots})
            if not updated_node:
                return None
            return updated_node
        except ValidationError as e:
            raise ValueError(f"Invalid job slots value: {str(e)}")
