from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class QuoteBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    region: Optional[str] = None
    preferred_language: Optional[str] = None
    company_name: Optional[str] = None
    request_details: Optional[str] = None
    country: Optional[str] = None
    work_address: Optional[str] = None
    phone: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    subscribe_updates: bool = False


class QuoteCreate(QuoteBase):
    pass


class QuoteResponse(QuoteBase):
    id: str
    created_at: datetime
