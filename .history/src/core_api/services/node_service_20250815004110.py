from typing import Optional
from pydantic import ValidationError
from ..db.node_database import NodeDatabase
from ..models.node import Node

class NodeService:
    def __init__(self):
        self.node_slots = {}

    def set_job_slots(self, node_id: str, slots: int) -> bool:
        if not isinstance(slots, int):
            raise ValueError("Job slots must be an integer")
        if slots < 0:
            raise ValueError("Job slots must be a non-negative integer")
        self.node_slots[node_id] = slots
        return True

