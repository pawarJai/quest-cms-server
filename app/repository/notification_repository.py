from app.config.database import db
from bson.objectid import ObjectId
from datetime import datetime

class NotificationRepository:

    @staticmethod
    async def create_notification(notification_data: dict):
        """
        notification_data should contain:
        {
            "user_email": str,
            "message": str,
            "type": str,  # e.g., 'product_created', 'file_uploaded'
            "created_at": datetime,
            "read": bool
        }
        """
        if "created_at" not in notification_data:
            notification_data["created_at"] = datetime.utcnow()
        if "read" not in notification_data:
            notification_data["read"] = False

        result = await db.notifications.insert_one(notification_data)
        return str(result.inserted_id)

    @staticmethod
    async def get_user_notifications(user_email: str):
        notifications = await db.notifications.find({"user_email": user_email}).sort("created_at", -1).to_list(100)
        for n in notifications:
            n["id"] = str(n["_id"])
            del n["_id"]
        return notifications

    @staticmethod
    async def mark_as_read(notification_id: str):
        await db.notifications.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"read": True}}
        )
        return True

    @staticmethod
    async def delete_notification(notification_id: str):
        await db.notifications.delete_one({"_id": ObjectId(notification_id)})
        return True
