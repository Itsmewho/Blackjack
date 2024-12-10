# Models
from pydantic import BaseModel, EmailStr, Field


class RegisterModel(BaseModel):
    name: str = Field(..., min_length=3)
    surname: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=4)
    sec_password: str = Field(..., min_length=4)


class UserModel(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    role: str


class AdminModel(BaseModel):
    name: str
    surname: str
    email: EmailStr
    role: str
