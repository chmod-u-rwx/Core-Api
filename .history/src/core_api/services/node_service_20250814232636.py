from typing import Optional
from pydantic import ValidationError
from ..db.node_database import NodeDatabase
from ..models.node import Node
import logging

class NodeService:
    def __init__(self, node_db: NodeDatabase):
        self.node_db = node_db
        self.logger = logging.getLogger(__name__)
    
    def set_job_slots(self, node_id: str, slots: int) -> Optional[Node]:
        try:
            self.logger.debug(f"Updating slots for node {node_id} to {slots}")
            
            
            if not isinstance(slots, int):
                raise ValueError("Job slots must be an integer")
                
            # Validate using Pydantic model
            Node(node_id=node_id, job_slots=slots)
            
            # Business logic validation
            if slots < 0:
                raise ValueError("Job slots cannot be negative")
                
            # Persist changes
            updated = self.node_db.update_node(node_id, {"job_slots": slots})
            
            if updated:
                self.logger.info(f"Successfully updated node {node_id} slots to {slots}")
            else:
                self.logger.warning(f"Node {node_id} not found")
                
            return updated
            
        except ValidationError as e:
            error_msg = f"Invalid job slots value: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)