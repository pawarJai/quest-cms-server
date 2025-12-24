from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List

from app.schemas.about_schema import AboutCreate, AboutUpdate
from app.repository.about_repository import AboutRepository
from app.repository.upload_repository import UploadRepository
from app.repository.notification_repository import NotificationRepository
from app.services.auth_dependency import verify_user

router = APIRouter(prefix="/about", tags=["About"])


# ----------------- FILE EXPAND HELPERS -----------------

async def expand_file(file_id: str):
    if not file_id:
        return None
    f = await UploadRepository.get_file_by_id(file_id)
    if not f:
        return None
    return {
        "id": f["_id"],
        "filename": f["filename"],
        "content": f["content"]
    }


async def expand_files(file_ids: List[str]):
    return [await expand_file(fid) for fid in file_ids if fid]


async def expand_about(doc: dict):
    if doc.get("about_video"):
        doc["about_video"] = await expand_file(doc["about_video"])

    doc["product_images"] = await expand_files(doc.get("product_images", []))

    for i in doc.get("industries_served", []):
        i["image"] = await expand_file(i.pop("image_id"))

    for g in doc.get("gallery", []):
        g["file"] = await expand_file(g.pop("file_id"))

    return doc


# ----------------- CREATE -----------------

@router.post("/", dependencies=[Depends(verify_user)])
async def create_about(payload: AboutCreate, user=Depends(verify_user)):
    about_id = await AboutRepository.create_about(payload.dict())

    about = await AboutRepository.get_by_id(about_id)
    about = await expand_about(about)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"About page '{payload.title}' created",
        "type": "about_created",
        "created_at": datetime.utcnow()
    })

    return {
        "message": "About page created",
        "about_id": about_id,
        "about": about
    }


# ----------------- GET ALL (PAGINATED) -----------------

@router.get("/", dependencies=[Depends(verify_user)])
async def get_all_about(page: int = 1, limit: int = 10):
    skip = (page - 1) * limit

    data = await AboutRepository.get_all(skip, limit)
    total = await AboutRepository.count()

    expanded = [await expand_about(d) for d in data]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "about_pages": expanded
    }


# ----------------- GET ONE -----------------

@router.get("/{about_id}", dependencies=[Depends(verify_user)])
async def get_about(about_id: str):
    about = await AboutRepository.get_by_id(about_id)
    if not about:
        raise HTTPException(404, "About page not found")

    return await expand_about(about)


# ----------------- UPDATE -----------------

@router.put("/{about_id}", dependencies=[Depends(verify_user)])
async def update_about(
    about_id: str,
    payload: AboutUpdate,
    user=Depends(verify_user)
):
    existing = await AboutRepository.get_by_id(about_id)
    if not existing:
        raise HTTPException(404, "About page not found")

    update_data = payload.dict(exclude_unset=True)

    if "product_images" in update_data:
        keep = update_data["product_images"].get("keep", [])
        new = update_data["product_images"].get("new_uploaded_ids", [])
        update_data["product_images"] = keep + new

    about = await AboutRepository.update(about_id, update_data)
    about = await expand_about(about)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"About page '{about.get('title')}' updated",
        "type": "about_updated",
        "created_at": datetime.utcnow()
    })

    return {
        "message": "About page updated",
        "about": about
    }


# ----------------- DELETE -----------------

@router.delete("/{about_id}", dependencies=[Depends(verify_user)])
async def delete_about(about_id: str, user=Depends(verify_user)):
    about = await AboutRepository.get_by_id(about_id)
    if not about:
        raise HTTPException(404, "About page not found")

    await AboutRepository.delete(about_id)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"About page '{about.get('title')}' deleted",
        "type": "about_deleted",
        "created_at": datetime.utcnow()
    })

    return {"message": "About page deleted"}
