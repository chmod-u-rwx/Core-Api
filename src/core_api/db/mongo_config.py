from pydantic import BaseModel
import os

class MongoConfig(BaseModel):
    uri: str
    database_name: str
    connect_timeout_ms: int = 5000

    @classmethod
    def from_env(cls):
        """For .env variable"""
        
        uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
        database_name = os.environ.get("MONGODB_DATABASE", "test_db")
        connect_timeout_ms = int(os.environ.get("MONGODB_CONNECT_TIMEOUT_MS", 5000))
        
        return cls(
            uri=uri,
            database_name=database_name,
            connect_timeout_ms=connect_timeout_ms,
        )