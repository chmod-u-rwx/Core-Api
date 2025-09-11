from typing import Any
from fastapi.testclient import TestClient
from mongomock import MongoClient
from unittest.mock import patch
from src.core_api.models.users import UserCreate, UserRoleEnum
from src.core_api.app import app
import pytest
import mongomock

@pytest.fixture
def client():
    with patch("src.core_api.db.users_db.get_mongo_client") as mock_get_client:
        mock_client: MongoClient[Any] = mongomock.MongoClient()
        mock_get_client.return_value = mock_client
        yield TestClient(app)

def create_user_data(
    username: str= "testuser",
    email: str = "test@example.com",
    password: str = "password123", 
    role: UserRoleEnum=UserRoleEnum.individual
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

def test_signup_success(client: Any):
    user_data = create_user_data().model_dump(mode="json")
    resp = client.post("/users/signup", json=user_data)
    assert resp.status_code == 200
    assert resp.json()["username"] == user_data["username"]
    assert resp.json()["email"] == user_data["email"]

def test_signup_password_mismatch(client: Any):
    user_data = create_user_data().model_dump(mode="json")
    user_data["confirm_password"] = "wrongpassword"
    resp = client.post("/users/signup", json=user_data)
    assert resp.status_code == 400
    assert "Passwords do not match" in resp.json()["detail"]

def test_signup_duplicate_user(client: Any):
    user_data = create_user_data().model_dump(mode="json")
    resp1 = client.post("/users/signup", json=user_data)
    assert resp1.status_code == 200
    resp2 = client.post("/users/signup", json=user_data)
    assert resp2.status_code == 400

def test_login_success(client: Any):
    user_data = create_user_data().model_dump(mode="json")
    client.post("/users/signup", json=user_data)
    credentials = {"email": user_data["email"], "password": user_data["password"]}
    resp = client.post("/users/login", json=credentials)
    assert resp.status_code == 200
    assert resp.json()["username"] == user_data["username"]

def test_login_wrong_password(client: Any):
    user_data = create_user_data().model_dump(mode="json")
    client.post("/users/signup", json=user_data)
    credentials: dict[str, str] = {"email": user_data["email"], "password": "wrongpassword"}
    resp = client.post("/users/login", json=credentials)
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]

def test_login_nonexistent_email(client: Any):
    credentials = {"email": "noone@example.com", "password": "password123"}
    resp = client.post("/users/login", json=credentials)
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]