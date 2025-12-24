from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: Optional[str] = None
    first_name: str
    last_name: str
    company: Optional[str] = None
    email: EmailStr
    hashed_password: str

    last_login: Optional[datetime] = None
    last_logout: Optional[datetime] = None

    is_email_verified: bool = False

    otp: Optional[str] = None
    otp_created_at: Optional[datetime] = None

    created_at: datetime = datetime.utcnow()


class Admin(BaseModel):
    email: EmailStr
    password: str
    exists: Optional[bool] = False
