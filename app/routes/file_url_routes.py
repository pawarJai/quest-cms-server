from fastapi import APIRouter, HTTPException
from app.repository.file_url_repository import FileUrlRepository

router = APIRouter(prefix="/file-urls", tags=["File URLs"])

@router.get("/{file_id}")
async def get_file_url(file_id: str):
    doc = await FileUrlRepository.get_url_by_file_id(file_id)
    if not doc:
        raise HTTPException(404, "File URL not found")
    return {
        "file_id": doc.get("file_id") or file_id,
        "filename": doc.get("filename"),
        "url": doc.get("url"),
        "type": doc.get("type")
    }
