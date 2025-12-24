from fastapi import APIRouter, Depends
from app.repository.notification_repository import NotificationRepository
from app.schemas.notification_schema import NotificationOut, NotificationCreate
from app.services.auth_dependency import verify_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# ------------------------- CREATE NOTIFICATION -------------------------
@router.post("/", dependencies=[Depends(verify_user)])
async def create_notification(message: str, type: str, payload=Depends(verify_user)):
    """
    Create a notification for the logged-in user.
    """
    user_email = payload["sub"]
    notification = NotificationCreate(user_email=user_email, message=message, type=type)
    notification_id = await NotificationRepository.create_notification(notification)
    return {"message": "Notification created", "notification_id": notification_id}

# ------------------------- GET USER NOTIFICATIONS -------------------------
@router.get("/", dependencies=[Depends(verify_user)], response_model=list[NotificationOut])
async def get_notifications(payload=Depends(verify_user)):
    user_email = payload["sub"]
    notifications = await NotificationRepository.get_user_notifications(user_email)
    return notifications

# ------------------------- MARK NOTIFICATION AS READ -------------------------
@router.put("/{notification_id}/read", dependencies=[Depends(verify_user)])
async def mark_notification_read(notification_id: str):
    await NotificationRepository.mark_as_read(notification_id)
    return {"message": "Notification marked as read"}
