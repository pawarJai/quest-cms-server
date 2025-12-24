from app.config.database import db
import uuid
import base64

class UploadRepository:

    COLLECTION = db["files"]  # <--- single source of truth

    @staticmethod
    async def save_file(filename: str, content_bytes: bytes):
        file_id = str(uuid.uuid4())
        b64 = base64.b64encode(content_bytes).decode("utf-8")

        file_doc = {
            "_id": file_id,
            "filename": filename,
            "content": b64
        }

        await UploadRepository.COLLECTION.insert_one(file_doc)
        return file_id

    @staticmethod
    async def get_file(file_id: str):
        return await UploadRepository.COLLECTION.find_one({"_id": file_id})

    @staticmethod
    async def get_file_by_id(file_id: str):
        return await UploadRepository.COLLECTION.find_one({"_id": file_id})
