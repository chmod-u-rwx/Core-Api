from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class UserRoleEnum(str, Enum):
    individual = "individual"
    company = "company"

class Users(BaseModel):
    user_id: Optional[UUID] = Field(default=None)
    username: str = Field(..., min_length=1, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=1, max_length=100)
    role: UserRoleEnum = Field(...)

class IndividualUserCredentials(Users):
    password: str = Field(...)
    confirm_password: str = Field(...)
    role: UserRoleEnum = Field(default=UserRoleEnum.individual)

class CompanyUserCredentials(Users):
    companyName: str = Field(..., min_length=1, max_length=100)
    companyAddress: str = Field(..., min_length=1, max_length=100)
    password: str = Field(...)
    confirmPassword: str = Field(...)
    role: UserRoleEnum = Field(default=UserRoleEnum.company)

class UserAuth(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(...)
    username: str = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: EmailStr = Field(...)
    phone_number: str = Field(...)
    user_id: UUID = Field(...)
    role: UserRoleEnum = Field(...)
    company_name: Optional[str] = Field(default=None)
    company_address: Optional[str] = Field(default=None)

class LoginCredentials(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    username: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, min_length=1, max_length=100)
    password: Optional[str] = Field(default=None, min_length=1, max_length=100)