from uuid import uuid4
from src.core_api.utils.jwt import create_access_token
from src.core_api.utils.security import hash_password, verify_password
from src.core_api.models.users import LoginCredentials, UserAuth, UserCreate, Users
from src.core_api.db.users_db import UserNotFoundException, UsersDatabase

class UsersService:
    def __init__(self) -> None:
        self.db = UsersDatabase()
    
    def signup(self, user_data: UserCreate) -> Users:
        if user_data.password != user_data.confirm_password:
            raise ValueError("Passwords do not match")
        
        password_hashed = hash_password(user_data.password)
        user_dict = user_data.model_dump(exclude={"confirm_password"})
        user_dict["password"] = password_hashed
        user_dict["user_id"] = uuid4()
        
        user = Users(**{**user_dict})
        return self.db.create(user)
    
    def login(self, credentials: LoginCredentials) -> UserAuth:
        try:
            user = self.db.get_by_email(credentials.email)
        except UserNotFoundException:
            raise ValueError("Invalid email or password")
        
        if not verify_password(credentials.password, getattr(user, "password", "")):
            raise ValueError("Invalid email or password")
        
        token = create_access_token(user)
        return UserAuth(
            access_token=token,
            token_type="bearer",
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone_number=user.phone_number,
            user_id=user.user_id,
            role=user.role,
            company_name=user.company_name,
            company_address=user.company_address,
        )