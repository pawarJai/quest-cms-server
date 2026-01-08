from app.config.database import db
import uuid
from datetime import datetime

COLLECTION = db["quotes"]


class QuoteRepository:

    @staticmethod
    async def create_quote(data: dict):
        data["_id"] = str(uuid.uuid4())
        data["created_at"] = datetime.utcnow()
        await COLLECTION.insert_one(data)
        return data["_id"]

    @staticmethod
    async def get_all_quotes():
        return await COLLECTION.find().sort("created_at", -1).to_list(None)

    @staticmethod
    async def get_quote_by_id(quote_id: str):
        return await COLLECTION.find_one({"_id": quote_id})
