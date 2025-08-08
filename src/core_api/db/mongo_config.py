from pydantic import BaseModel
import os

class MongoConfig(BaseModel):
    uri: str
    database_name: str
    connect_timeout_ms: int = 5000

    @classmethod
    def from_env(cls, database_name: str, connect_timeout_ms: int = 5000):
        """Just add the database name"""
        
        uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
        return cls(
            uri=uri,
            database_name=database_name,
            connect_timeout_ms=connect_timeout_ms,
        )