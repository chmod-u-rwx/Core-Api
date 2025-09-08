from src.core_api.models.users import UserUpdate, Users
from src.core_api.db.users_db import UsersDatabase

class UsersService:
    def __init__(self) -> None:
        self.db = UsersDatabase()
    
    # def create_users(self, )
    
    def get_username(self, username: str) -> Users:
        return self.db.get_by_username(username)
    
    def get_email(self, email: str) -> Users:
        return self.db.get_by_email(email)
    
    # def list_users(
    #     self
    # )
    
    def update_users(self, username: str, update_data: UserUpdate) -> Users:
        return self.db.update(username, update_data)
    
    # def 