from threading import Lock

from pydantic import UUID4
from src.core_api.db.master_node_db import MasterNodeDatabase, MasterNodeNotFoundException
from src.core_api.models.master_node import MasterNode

class MasterNodeService:
    _rr_lock = Lock()
    _rr_index = [0]
    
    def __init__(self) -> None:
        self.db = MasterNodeDatabase()
    
    def register(self, node: MasterNode) -> MasterNode:
        try:
            return self.db.create(node)
        except Exception as e:
            raise RuntimeError(f"Failed to register master node: {e}")
    
    def discover(self) -> MasterNode:
        """
        Round-robin discovery of a master node.
        Picks the next available node from the list
        """
        nodes = self.db.list_all()
        if not nodes:
            raise MasterNodeNotFoundException("No master node available")
        
        nodes.sort(key=lambda n: str(n.master_id))
        
        with self._rr_lock:
            idx = self._rr_index[0] % len(nodes)
            self._rr_index[0] += 1
        
        return nodes[idx]
    
    def unregister(self, master_id: UUID4) -> bool:
        return self.db.delete(master_id)