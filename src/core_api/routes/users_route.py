from fastapi import APIRouter, HTTPException

from src.core_api.services.users_service import UsersService
from src.core_api.models.users import LoginCredentials, UserAuth, UserCreate, Users

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/signup", response_model=Users)
def signup(user: UserCreate):
    try:
        return UsersService().signup(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=UserAuth)
def login(user: LoginCredentials):
    try:
        return UsersService().login(user)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))