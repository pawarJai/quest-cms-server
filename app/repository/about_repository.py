from app.config.database import db
import uuid

COLLECTION = db["about"]

class AboutRepository:

    @staticmethod
    async def create_about(doc: dict):
        doc["_id"] = str(uuid.uuid4())
        await COLLECTION.insert_one(doc)
        return doc["_id"]

    @staticmethod
    async def get_all(skip=0, limit=10):
        return await COLLECTION.find().skip(skip).limit(limit).to_list(limit)

    @staticmethod
    async def count():
        return await COLLECTION.count_documents({})

    @staticmethod
    async def get_by_id(about_id: str):
        return await COLLECTION.find_one({"_id": about_id})

    @staticmethod
    async def update(about_id: str, update_data: dict):
        await COLLECTION.update_one({"_id": about_id}, {"$set": update_data})
        return await COLLECTION.find_one({"_id": about_id})

    @staticmethod
    async def delete(about_id: str):
        result = await COLLECTION.delete_one({"_id": about_id})
        return result.deleted_count > 0
