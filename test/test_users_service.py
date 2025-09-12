from typing import Any
import mongomock
import pytest
from unittest.mock import patch
from mongomock import MongoClient
from src.core_api.models.users import LoginCredentials, UserAuth, UserCreate, UserRoleEnum
from src.core_api.services.users_service import UsersService

@pytest.fixture
def user_service():
    with patch("src.core_api.db.users_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        yield UsersService()

def create_user(
    username: str="testuser",
    email: str="test@example.com",
    password: str="password123",
    role: UserRoleEnum=UserRoleEnum.INDIVIDUAL
) -> UserCreate:
    return UserCreate(
        username=username,
        first_name="Test",
        last_name="User",
        email=email,
        phone_number="09123456789",
        role=role,
        password=password,
        confirm_password=password
    )

def test_signup_success(user_service: UsersService):
    user_data = create_user()
    user = user_service.signup(user_data)
    assert user.username == user_data.username
    assert user.email == user_data.email
    assert user.role == user_data.role

def test_signup_password_mismatch(user_service: UsersService):
    user_data = create_user()
    user_data.confirm_password = "pass2"
    with pytest.raises(ValueError, match="Passwords do not match"):
        user_service.signup(user_data)

def test_signup_duplicate_user(user_service: UsersService):
    user_data = create_user()
    user_service.signup(user_data)
    with pytest.raises(ValueError):
        user_service.signup(user_data)

def test_login_success(user_service: UsersService):
    user_data = create_user()
    user_service.signup(user_data)
    credentials = LoginCredentials(email=user_data.email, password=user_data.password)
    auth = user_service.login(credentials)
    assert isinstance(auth, UserAuth)
    assert auth.username == user_data.username
    assert auth.access_token
    assert auth.token_type == "bearer"

def test_login_wrong_password(user_service: UsersService):
    user_data = create_user()
    user_service.signup(user_data)
    credentials = LoginCredentials(email=user_data.email, password="wrongpassword")
    with pytest.raises(ValueError, match="Invalid email or password"):
        user_service.login(credentials)

def test_login_nonexistent_email(user_service: UsersService):
    credentials = LoginCredentials(email="noone@example.com", password="password123")
    with pytest.raises(ValueError, match="Invalid email or password"):
        user_service.login(credentials)