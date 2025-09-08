from typing import Any, List
from uuid import uuid4
from pymongo import ASCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError
from pymongo.collection import Collection
from pymongo.database import Database

from src.core_api.models.users import UserUpdate, Users
from src.core_api.config import DATABASE_NAME
from src.core_api.db.connection import get_mongo_client

class UserNotFoundException(Exception):
    ...

class UsersDatabase:
    def __init__(
        self
        ) -> None:
            try:
                self.client = get_mongo_client()
                self.db: Database[Any] = self.client[DATABASE_NAME]
                self.collection: Collection[Any] = self.db["users"]
                self._create_indexes()
            except PyMongoError as e:
                raise RuntimeError(f"Database initialization failed: {e}")
            
    def _create_indexes(self) -> None:
        try:
            self.collection.create_index(
                [("username", ASCENDING)],
                name="idx_username",
                unique=True
            )
            self.collection.create_index(
                [("email", ASCENDING)],
                name="idx_email",
                unique=True
            )
        except PyMongoError as e:
            raise RuntimeError(f"Index creation failed: {e}")
    
    def create(self, user: Users) -> Users:
        try:
            user_data = user.model_dump(mode="json", by_alias=True)
            if "user_id" not in user_data or user_data["user_id"] is None:
                user_data["user_id"] = str(uuid4())
            
            result = self.collection.insert_one(user_data)
            if not result.inserted_id:
                raise RuntimeError("Failed to insert user: No inserted_id returned")
            
            inserted = self.collection.find_one({"_id": result.inserted_id})
            if not inserted:
                raise RuntimeError("Inserted user not found")
            inserted.pop("_id", None)
            
            return Users(**inserted)
        except DuplicateKeyError as e:
            raise ValueError(f"User is already existing: {e}")
        except PyMongoError as e:
            raise RuntimeError(f"Failed to craete user: {e}")
    
    def get_by_username(self, username: str) -> Users:
        try:
            doc = self.collection.find_one({"username": username})
            if not doc:
                raise UserNotFoundException(f"User: '{username}' not found")
            doc.pop("_id", None)
            return Users(**doc)
        except PyMongoError as e:
            raise RuntimeError(f"Failed to get username: {e}")
    
    def get_by_email(self, email: str) -> Users:
        try:
            doc = self.collection.find_one({"email": email})
            if not doc:
                raise UserNotFoundException(f"Email: '{email}' not found")
            doc.pop("_id", None)
            
            return Users(**doc)
        except PyMongoError as e:
            raise RuntimeError(f"Failed to get email: {e}")
    
    def list_all(self) -> List[Users]:
        try:
            docs = list(self.collection.find())
            for doc in docs:
                doc.pop("_id", None)
            return [Users(**doc) for doc in docs]
        except PyMongoError as e:
            raise RuntimeError(f"Failed to list to users: {e}")
    
    def update(self, username: str, updated: UserUpdate) -> Users:
        try:
            update_data = updated.model_dump(exclude_unset=True)
            if not update_data:
                raise ValueError("No fields to update")
            
            result = self.collection.update_one(
                {"username": username},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise UserNotFoundException(f"User with {username} is not found")
            
            return self.get_by_username(username)
        except PyMongoError as e:
            raise RuntimeError(f"Failed to update user: {e}")
        
    def delete(self, username: str) -> bool:
        try:
            result = self.collection.delete_one({"username": username})
            if result.deleted_count == 0:
                raise UserNotFoundException(f"User: '{username}' not found")
            
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RuntimeError(f"Failed to delete user: {e}")