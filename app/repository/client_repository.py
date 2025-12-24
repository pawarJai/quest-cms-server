from app.config.database import db
import uuid

COLLECTION = db["clients"]

class ClientRepository:

    @staticmethod
    async def create_client(doc: dict):
        doc["_id"] = doc.get("_id", str(uuid.uuid4()))
        await COLLECTION.insert_one(doc)
        return doc["_id"]

    @staticmethod
    async def get_all_clients():
        return await COLLECTION.find().to_list(None)

    @staticmethod
    async def get_client_by_id(client_id: str):
        return await COLLECTION.find_one({"_id": client_id})

    @staticmethod
    async def update_client(client_id: str, update_data: dict):
        await COLLECTION.update_one({"_id": client_id}, {"$set": update_data})
        return await COLLECTION.find_one({"_id": client_id})

    @staticmethod
    async def delete_client(client_id: str):
        result = await COLLECTION.delete_one({"_id": client_id})
        return result.deleted_count > 0
