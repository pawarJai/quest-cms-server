from pydantic import BaseModel
from datetime import datetime

class NotificationCreate(BaseModel):
    user_email: str
    message: str
    type: str  # e.g., 'product_created', 'file_uploaded'
    created_at: datetime = datetime.utcnow()
    read: bool = False

class NotificationOut(BaseModel):
    id: str
    user_email: str
    message: str
    type: str
    created_at: datetime
    read: bool
