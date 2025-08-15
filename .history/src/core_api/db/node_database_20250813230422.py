from models.node import Node
from typing import Dict, Optional, List
import uuid 

class NodeDatabase:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}  # node_id -> Node mapping

    # CREATE
    def create_node(self, node_data: dict) -> Node:
        """Create and store a new node"""
        node = Node(**node_data)  # Validates using Pydantic
        self._nodes[node.node_id] = node
        return node

    # READ
    def get_node(self, node_id: str) -> Node[Node]:
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