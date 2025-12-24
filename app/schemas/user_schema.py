from pydantic import BaseModel, EmailStr
from typing import Optional


class UserSignupSchema(BaseModel):
    firstname: str
    lastname: str
    company: Optional[str] = None
    email: EmailStr
    password: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
