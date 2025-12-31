from app.config.database import db
# from app.db.mongo import db
COLLECTION = db["file_urls"]
class FileUrlRepository:



    @staticmethod
    async def get_url_by_file_id(file_id: str):
        return await COLLECTION.find_one({"file_id": file_id})


    @staticmethod
    async def save_url(file_id: str, filename: str, url: str, file_type: str):
        await COLLECTION.insert_one({
            "file_id": file_id,
            "filename": filename,
            "url": url,
            "type": file_type
        })
