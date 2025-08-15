from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from ..db.connection import get_mongo_client
from ..config import DATABASE_CONNECT_TIMEOUT, DATABASE_URL 


class NodeDataBase:
    # initialize the existing db connection.py
    def __init__(self, db_name: str = "node_database"):
                 
        self.client = get_mongo_client()
        self.db = self.client[db_name]
        self.nodes: Collection = self.db.nodes
        self._initialize_collection()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _initialize_collection(self):
        try: #create index on node_id for uniqueness and fast lookups
            self.nodes.create_index([("node_id, 1")], unique=True, background=True)
            self.logger.info("Successful")
        except DuplicateKeyError:
            self.logger.warning("Existing index")
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to create index: {pymongo_error}")
            raise RuntimeError(f"Error with the database initialization: {pymongo_error}")
        
    def create(self, node: 'Node') -> bool:
        try:
            node_dict = self._node_to_dict(node)
            node_dict['created_at'] = datetime.utcnow()
            node_dict['updated_at'] = datetime.utcnow()

            result = self.nodes.insert_one(node_dict)
            return result.acknowledged
        except DuplicateKeyError:
            self.logger.error(f"Node with this ID {node.id}: already exists.")
            return False
        except PyMongoError as pymongo_error:
            self.logger.error(f"Failed to create node: {from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

# Import your existing connection setup
from .connection import get_mongo_client
from ..config import DATABASE_URL, DATABASE_CONNECT_TIMEOUT

class NodeDatabase:
    def __init__(self, db_name: str = "node_db"):
        """
        Initialize the MongoDB Node database using the existing connection setup.
        
        Args:
            db_name: Database name to use (default: "node_db")
        """
        self.client = get_mongo_client()
        self.db = self.client[db_name]
        self.nodes: Collection = self.db.nodes  # Collection for nodes with type hint
        self._initialize_collection()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
    def _initialize_collection(self) -> None:
        """Initialize the MongoDB collection with indexes and validation if needed."""
        try:
            # Create index on id for fast lookups
            self.nodes.create_index([("id", 1)], unique=True, background=True)
            
            # Create index on type for faster filtering
            self.nodes.create_index([("type", 1)], background=True)
            
            # Optional: Create compound indexes based on your query patterns
            # self.nodes.create_index([("type", 1), ("created_at", -1)], background=True)
            
            self.logger.info("Database indexes initialized successfully")
            
        except PyMongoError as e:
            self.logger.error(f"Failed to initialize database indexes: {e}")
            raise RuntimeError(f"Database initialization failed: {e}")
    
    def create(self, node: 'Node') -> bool:
        """
        Create a new node in the database.
        
        Args:
            node: The Node object to store
            
        Returns:
            bool: True if successful, False if node with same ID exists
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            node_dict = self._node_to_dict(node)
            node_dict['created_at'] = datetime.utcnow()
            node_dict['updated_at'] = datetime.utcnow()
            
            result = self.nodes.insert_one(node_dict)
            return result.acknowledged
            
        except DuplicateKeyError:
            self.logger.warning(f"Node with id {node.id} already exists")
            return False
        except PyMongoError as e:
            self.logger.error(f"Failed to create node {node.id}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")
    
    def read(self, node_id: str) -> Optional['Node']:
        """
        Retrieve a node from the database by its ID.
        
        Args:
            node_id: The ID of the node to retrieve
            
        Returns:
            The Node object if found, None otherwise
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            node_data = self.nodes.find_one({"id": node_id})
            if node_data:
                return self._dict_to_node(node_data)
            return None
        except PyMongoError as e:
            self.logger.error(f"Failed to read node {node_id}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")
    
    def read_all(self, filter: Optional[Dict] = None, 
                projection: Optional[Dict] = None,
                limit: int = 0) -> List['Node']:
        """
        Retrieve nodes from the database with optional filtering.
        
        Args:
            filter: Optional MongoDB query filter
            projection: Optional fields to include/exclude
            limit: Maximum number of nodes to return (0 for no limit)
            
        Returns:
            List of Node objects
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            if filter is None:
                filter = {}
            cursor = self.nodes.find(filter, projection).limit(limit)
            return [self._dict_to_node(node) for node in cursor]
        except PyMongoError as e:
            self.logger.error(f"Failed to read nodes: {e}")
            raise RuntimeError(f"Database operation failed: {e}")
    
    def update(self, node: 'Node', partial: bool = False) -> bool:
        """
        Update an existing node in the database.
        
        Args:
            node: The Node object with updated values
            partial: If True, only update provided fields
            
        Returns:
            bool: True if update was successful, False otherwise
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            update_data = {"$set": {"updated_at": datetime.utcnow()}}
            
            if partial:
                # For partial updates, only update the fields present in the node
                node_dict = self._node_to_dict(node)
                for field, value in node_dict.items():
                    if field not in ["id", "created_at"]:  # Never update these
                        update_data["$set"][field] = value
            else:
                # Full update - replace all fields except metadata
                node_dict = self._node_to_dict(node)
                node_dict["updated_at"] = datetime.utcnow()
                update_data = {"$set": node_dict}
                # Preserve created_at
                update_data["$setOnInsert"] = {"created_at": node_dict.get("created_at", datetime.utcnow())}
            
            result = self.nodes.update_one(
                {"id": node.id},
                update_data,
                upsert=False  # Don't create if doesn't exist
            )
            
            return result.modified_count > 0
            
        except PyMongoError as e:
            self.logger.error(f"Failed to update node {node.id}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")
    
    def delete(self, node_id: str) -> bool:
        """
        Delete a node from the database.
        
        Args:
            node_id: The ID of the node to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            result = self.nodes.delete_one({"id": node_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            self.logger.error(f"Failed to delete node {node_id}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")
    
    def count(self, filter: Optional[Dict] = None) -> int:
        """
        Count nodes matching optional filter.
        
        Args:
            filter: Optional MongoDB query filter
            
        Returns:
            int: Count of matching nodes
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            if filter is None:
                filter = {}
            return self.nodes.count_documents(filter)
        except PyMongoError as e:
            self.logger.error(f"Failed to count nodes: {e}")
            raise RuntimeError(f"Database operation failed: {e}")
    
    def _node_to_dict(self, node: 'Node') -> Dict[str, Any]:
        """
        Convert a Node object to a dictionary for MongoDB storage.
        
        Args:
            node: The Node object to convert
            
        Returns:
            Dictionary representation of the Node
        """
        # Handle different Node class implementations
        if hasattr(node, 'dict'):
            return node.dict()
        elif hasattr(node, '__dict__'):
            return vars(node).copy()
        elif hasattr(node, 'model_dump'):  # For Pydantic v2
            return node.model_dump()
        else:
            raise ValueError("Unsupported Node type - cannot convert to dictionary")
    
    def _dict_to_node(self, node_dict: Dict[str, Any]) -> 'Node':
        """
        Convert a MongoDB document to a Node object.
        
        Args:
            node_dict: Dictionary from MongoDB
            
        Returns:
            Reconstructed Node object
        """
        from your_module import Node  # Import your actual Node class
        
        # Remove MongoDB-specific fields if present
        node_dict.pop('_id', None)
        
        # Handle different Node class initialization methods
        if hasattr(Node, 'parse_obj'):  # Pydantic v1
            return Node.parse_obj(node_dict)
        elif hasattr(Node, 'model_validate'):  # Pydantic v2
            return Node.model_validate(node_dict)
        else:
            return Node(**node_dict)
    
    def close(self) -> None:
        """Close the MongoDB connection."""
        try:
            self.client.close()
            self.logger.info("Database connection closed successfully")
        except PyMongoError as e:
            self.logger.error(f"Failed to close database connection: {e}")
    
    def __enter__(self):
        """Support for context manager protocol."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager protocol."""
        self.close()}")
            raise RuntimeError(f"Error creating node: {e}")
