import mongomock
import pytest
from typing import Any
from unittest.mock import patch
from mongomock import MongoClient
from src.core_api.db.users_db import UserNotFoundException, UsersDatabase
from src.core_api.models.users import UserRoleEnum, UserUpdate, Users

@pytest.fixture
def users_db():
    with patch("src.core_api.db.users_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        db = UsersDatabase()
        yield db

def create_individual_user(username: str = "dame_un_grr", email: str = "test@example.com") -> Users:
    return Users(
        user_id=None,
        username=username,
        first_name="Test",
        last_name="User",
        email=email,
        phone_number="09123456789",
        role=UserRoleEnum.individual
    )

def test_create_indiv_user(users_db: UsersDatabase):
    user = create_individual_user()
    created = users_db.create(user)
    assert created.username == user.username
    assert created.email == user.email

def test_create_duplicate_user(users_db: UsersDatabase):
    user = create_individual_user()
    users_db.create(user)
    with pytest.raises(ValueError):
        users_db.create(user)

def test_get_by_username_success(users_db: UsersDatabase):
    user = create_individual_user()
    users_db.create(user)
    fetched = users_db.get_by_username(user.username)
    assert fetched.username == user.username

def test_get_by_username_not_found(users_db: UsersDatabase):
    with pytest.raises(UserNotFoundException):
        users_db.get_by_username("nonexistent")

def test_get_by_email_success(users_db: UsersDatabase):
    user = create_individual_user()
    users_db.create(user)
    fetched = users_db.get_by_email(user.email)
    assert fetched.email == user.email

def test_list_all(users_db: UsersDatabase):
    user1 = create_individual_user(username="user1", email="user1@example.com")
    user2 = create_individual_user(username="user2", email="user2@example.com")
    users_db.create(user1)
    users_db.create(user2)
    all_users = users_db.list_all()
    usernames = {u.username for u in all_users}
    assert "user1" in usernames
    assert "user2" in usernames
    assert len(all_users) == 2

def test_update_user_success(users_db: UsersDatabase):
    user = create_individual_user()
    users_db.create(user)
    update = UserUpdate(first_name="Updated", last_name="Name")
    updated = users_db.update(user.username, update)
    assert updated.first_name == "Updated"
    assert updated.last_name == "Name"

def test_update_user_no_fields(users_db: UsersDatabase):
    user = create_individual_user()
    users_db.create(user)
    update = UserUpdate()
    with pytest.raises(ValueError):
        users_db.update(user.username, update)

def test_update_user_not_found(users_db: UsersDatabase):
    update = UserUpdate(first_name="Updated")
    with pytest.raises(UserNotFoundException):
        users_db.update("nonexistent", update)

def test_delete_user_success(users_db: UsersDatabase):
    user = create_individual_user()
    users_db.create(user)
    assert users_db.delete(user.username) is True
    with pytest.raises(UserNotFoundException):
        users_db.get_by_username(user.username)

def test_delete_user_not_found(users_db: UsersDatabase):
    with pytest.raises(UserNotFoundException):
        users_db.delete("nonexistent")