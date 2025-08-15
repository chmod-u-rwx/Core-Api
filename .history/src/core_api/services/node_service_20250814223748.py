from typing import Optional
from ..dbnode_database import NodeDatabase
from src.models.node import Node


class NodeService:
    def __init__(self, node_db: NodeDatabase):
        self.node_db = node_db

    def set_available_job_slots(self, node_id: str, new_slots: int) -> Optional[Node]:
        """
        Update the available job slots for a node.

        Args:
            node_id (str): The ID of the node to update.
            new_slots (int): The new number of job slots (must be >= 0).

        Returns:
            Optional[Node]: The updated node object, or None if not found.
        """
        if new_slots < 0:
            raise ValueError("Job slots cannot be negative.")

        return self.node_db.update_node(node_id, {"job_slots": new_slots})
