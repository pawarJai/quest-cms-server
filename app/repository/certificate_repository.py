from app.config.database import db
import uuid

COLLECTION = db["certifications"]

class CertificateRepository:

    @staticmethod
    async def create_certificate(doc: dict):
        doc["_id"] = doc.get("_id", str(uuid.uuid4()))
        await COLLECTION.insert_one(doc)
        return doc["_id"]

    @staticmethod
    async def get_all_certificates():
        return await COLLECTION.find().to_list(None)

    @staticmethod
    async def get_certificate_by_id(cert_id: str):
        return await COLLECTION.find_one({"_id": cert_id})

    @staticmethod
    async def update_certificate(cert_id: str, update_data: dict):
        await COLLECTION.update_one({"_id": cert_id}, {"$set": update_data})
        return await COLLECTION.find_one({"_id": cert_id})

    @staticmethod
    async def delete_certificate(cert_id: str):
        result = await COLLECTION.delete_one({"_id": cert_id})
        return result.deleted_count > 0
