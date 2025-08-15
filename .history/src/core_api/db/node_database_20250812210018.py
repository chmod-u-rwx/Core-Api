# db/node_database.py
from typing import Dict, Optional
from models.node import Node, NodeInDB

class NodeDatabase:
    def __init__(self):
        # In-memory store for nodes
        self.nodes: Dict[str, NodeInDB] = {}

    def create_node(self, node: Node) -> NodeInDB:
        node_in_db = NodeInDB(**node.dict())
        self.nodes[node_in_db.id] = node_in_db
        return node_in_db

    def get_node(self, node_id: str) -> Optional[NodeInDB]:
        return self.nodes.get(node_id)

    def update_node(self, node_id: str, job_slots: int) -> Optional[NodeInDB]:
        node = self.nodes.get(node_id)
        if node:
            node.job_slots = job_slots
        return node

    def delete_node(self, node_id: str) -> bool:
        return self.nodes.pop(node_id, None) is not None

    def list_nodes(self) -> list[NodeInDB]:
        return list(self.nodes.values())
