from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from src.core_api.models.users import Users
from ..config import JWT_SECRET_KEY

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(user: Users, expires_delta: Optional[timedelta] = None) -> str:
    if JWT_SECRET_KEY is None:
        raise ValueError("JWT_SECRET_KEY must not be None")
    
    expire: datetime = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    payload: dict[str, str | int] = {
        "sub": user.username,
        "user_id": str(user.user_id),
        "role": user.role.value,
        "exp": int(expire.timestamp()),
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)