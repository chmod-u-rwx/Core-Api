from typing import Optional
from pydantic import ValidationError
from ..db.node_database import NodeDatabase
from ..models.node import Node

class NodeService:
    """Service layer for node operations with business logic"""
    
    def __init__(self, node_db: NodeDatabase):
        """
        Initialize with a NodeDatabase instance
        
        Args:
            node_db: Injected database dependency
        """
        self.node_db = node_db

    def set_job_slots(self, node_id: str, slots: int) -> Optional[Node]:
        """
        Set available job slots for a node with validation
        
        Args:
            node_id: Target node identifier
            slots: New job slots value (must be >= 0)
            
        Returns:
            Updated Node if successful, None if node not found
            
        Raises:
            ValueError: If slots value is invalid
        """
        try:
            # Validate slots value first
            Node(node_id=node_id, job_slots=slots)  # Triggers Pydantic validation
            
            # Update only if validation passes
            return self.node_db.update_node(node_id, {"job_slots": slots})
        except ValidationError as e:
            raise ValueError(f"Invalid job slots value: {str(e)}")

    # Future-ready architecture patterns:
    # 1. Method stubs for planned features
    # 2. Type hints for all parameters/returns
    # 3. Dependency injection
    # 4. Clear separation of concerns
    
    # Example future methods (unimplemented):
    # def allocate_job(self, node_id: str) -> bool:
    # def release_job_slot(self, node_id: str) -> bool:
    # def get_available_nodes(self, min_slots: int) -> List[Node]: