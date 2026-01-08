from fastapi import APIRouter, HTTPException, Request
from app.repository.file_url_repository import FileUrlRepository
from app.services.cloudinary_service import ensure_accessible_url

router = APIRouter(prefix="/file-urls", tags=["File URLs"])

@router.get("/{file_id}")
async def get_file_url(file_id: str, request: Request):
    doc = await FileUrlRepository.get_url_by_file_id(file_id)
    if not doc:
        raise HTTPException(404, "File URL not found")
    url_value = doc.get("url")
    if isinstance(url_value, str) and url_value.startswith("/"):
        url_value = str(request.base_url) + url_value.lstrip("/")
    else:
        url_value = ensure_accessible_url(url_value)
    return {
        "file_id": doc.get("file_id") or file_id,
        "filename": doc.get("filename"),
        "url": url_value,
        "type": doc.get("type")
    }
