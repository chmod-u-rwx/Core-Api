from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from models.node import Node
import uuid

class NodeDatabase:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}  # node_id -> Node mapping

    # CREATE
    def create_node(self, node_data: dict) -> Node:
        """Create and store a new node"""
        if 'node_id' not in node_data:
            node_data['node_id'] = str(uuid.uuid4())  # Auto-generate ID if not provided

        # Ensure node_id is a string
        if 'node_id' in node_data:
            node_data['node_id'] = str(node_data['node_id'])

        # Ensure job_slots is an int if present
        if 'job_slots' in node_data:
            try:
                node_data['job_slots'] = int(node_data['job_slots'])
            except (ValueError, TypeError):
                node_data['job_slots'] = 0  # or handle as appropriate

        node = Node(**node_data)
        self.nodes[node.node_id] = node
        return node

    # READ
    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node by ID"""
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> List[Node]:
        """Retrieve all nodes"""
        return list(self.nodes.values())

    # UPDATE
    def update_node(self, node_id: str, update_data: dict) -> Optional[Node]:
        """Update node attributes"""
        if node_id not in self.nodes:
            return None

        # Get existing data and merge with updates
        existing_data = self.nodes[node_id].dict()
        updated_data = {**existing_data, **update_data}
        
        # Validate and update
        updated_node = Node(**updated_data)
        self.nodes[node_id] = updated_node
        return updated_node

    # DELETE
    def delete_node(self, node_id: str) -> bool:
        """Remove a node by ID"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            return True
        return False

    # UTILITY METHODS
    def node_exists(self, node_id: str) -> bool:
        """Check if a node exists"""
        return node_id in self.nodes

    def count_nodes(self) -> int:
        """Get total number of nodes"""
        return len(self.nodes)