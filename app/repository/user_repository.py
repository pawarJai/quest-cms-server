from app.config.database import db 
from app.models.user_model import User


class UserRepository:
    #new provided methods
    @staticmethod
    async def create_user(user: dict):
        return await db.users.insert_one(user)

    @staticmethod
    async def get_user_by_email(email: str):
        return await db.users.find_one({"email": email})

    @staticmethod
    async def update_login(email: str, time):
        return await db.users.update_one(
            {"email": email},
            {"$set": {"last_login": time}}
        )
