from app.config.database import db
import uuid

COLLECTION = db["industries"]

class IndustryRepository:

    @staticmethod
    async def create_industry(doc: dict):
        doc["_id"] = doc.get("_id", str(uuid.uuid4()))
        await COLLECTION.insert_one(doc)
        return doc["_id"]

    @staticmethod
    async def get_all_industries():
        return await COLLECTION.find().to_list(None)

    @staticmethod
    async def get_industry_by_id(ind_id: str):
        return await COLLECTION.find_one({"_id": ind_id})

    @staticmethod
    async def update_industry(ind_id: str, update_data: dict):
        await COLLECTION.update_one({"_id": ind_id}, {"$set": update_data})
        return await COLLECTION.find_one({"_id": ind_id})

    @staticmethod
    async def delete_industry(ind_id: str):
        result = await COLLECTION.delete_one({"_id": ind_id})
        return result.deleted_count > 0
