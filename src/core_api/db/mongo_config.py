from pydantic import BaseModel

class MongoConfig(BaseModel):
    uri: str
    database_name: str
    connect_timeout_ms: int = 5000