# Models
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterModel(BaseModel):
    name: str = Field(..., min_length=3)
    surname: str = Field(..., min_length=3)
    email: EmailStr
    phone: str
    password: str = Field(..., min_length=4)
    sec_password: str = Field(..., min_length=4)


class UserModel(BaseModel):
    name: str
    surname: str
    email: EmailStr
    phone: int
    password: str
    sec_password: str
    role: Optional[str] = "user"
