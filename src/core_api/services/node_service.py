from uuid import UUID
from ..db.node_database import NodeDatabase
from ..models.node_model import Node, NodeUpdates

class NodeService:
    def __init__(self, node_db: NodeDatabase):
        self.db = node_db

    def update_node(self, node_id: UUID, node_updates: NodeUpdates) -> Node:
        return self.db.update_node(node_id, node_updates)
    