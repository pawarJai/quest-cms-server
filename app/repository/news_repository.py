from app.config.database import db
import uuid

COLLECTION = db["news"]


class NewsRepository:

    @staticmethod
    async def create_news(doc: dict):
        doc["_id"] = doc.get("_id", str(uuid.uuid4()))
        await COLLECTION.insert_one(doc)
        return doc["_id"]

    @staticmethod
    async def get_all_news():
        return await COLLECTION.find().to_list(None)

    @staticmethod
    async def get_news_by_id(news_id: str):
        return await COLLECTION.find_one({"_id": news_id})

    @staticmethod
    async def update_news(news_id: str, update_data: dict):
        await COLLECTION.update_one(
            {"_id": news_id},
            {"$set": update_data}
        )
        return await COLLECTION.find_one({"_id": news_id})

    @staticmethod
    async def delete_news(news_id: str):
        result = await COLLECTION.delete_one({"_id": news_id})
        return result.deleted_count > 0
