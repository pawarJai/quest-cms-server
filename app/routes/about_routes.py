# from fastapi import APIRouter, HTTPException, Depends
# from datetime import datetime
# from typing import List

# from app.schemas.about_schema import AboutCreate, AboutUpdate
# from app.repository.about_repository import AboutRepository
# from app.repository.upload_repository import UploadRepository
# from app.repository.notification_repository import NotificationRepository
# from app.services.auth_dependency import verify_user

# router = APIRouter(prefix="/about", tags=["About"])


# # ----------------- FILE EXPAND HELPERS -----------------

# async def expand_file(file_id: str):
#     if not file_id:
#         return None
#     f = await UploadRepository.get_file_by_id(file_id)
#     if not f:
#         return None
#     return {
#         "id": f["_id"],
#         "filename": f["filename"],
#         "content": f["content"]
#     }


# async def expand_files(file_ids: List[str]):
#     return [await expand_file(fid) for fid in file_ids if fid]


# async def expand_about(doc: dict):
#     if doc.get("about_video"):
#         doc["about_video"] = await expand_file(doc["about_video"])

#     doc["product_images"] = await expand_files(doc.get("product_images", []))

#     for i in doc.get("industries_served", []):
#         i["image"] = await expand_file(i.pop("image_id"))

#     for g in doc.get("gallery", []):
#         g["file"] = await expand_file(g.pop("file_id"))

#     return doc


# # ----------------- CREATE -----------------

# @router.post("/", dependencies=[Depends(verify_user)])
# async def create_about(payload: AboutCreate, user=Depends(verify_user)):
#     about_id = await AboutRepository.create_about(payload.dict())

#     about = await AboutRepository.get_by_id(about_id)
#     about = await expand_about(about)

#     await NotificationRepository.create_notification({
#         "user_email": user["sub"],
#         "message": f"About page '{payload.title}' created",
#         "type": "about_created",
#         "created_at": datetime.utcnow()
#     })

#     return {
#         "message": "About page created",
#         "about_id": about_id,
#         "about": about
#     }


# # ----------------- GET ALL (PAGINATED) -----------------

# @router.get("/", dependencies=[Depends(verify_user)])
# async def get_all_about(page: int = 1, limit: int = 10):
#     skip = (page - 1) * limit

#     data = await AboutRepository.get_all(skip, limit)
#     total = await AboutRepository.count()

#     expanded = [await expand_about(d) for d in data]

#     return {
#         "page": page,
#         "limit": limit,
#         "total": total,
#         "about_pages": expanded
#     }


# # ----------------- GET ONE -----------------

# @router.get("/{about_id}", dependencies=[Depends(verify_user)])
# async def get_about(about_id: str):
#     about = await AboutRepository.get_by_id(about_id)
#     if not about:
#         raise HTTPException(404, "About page not found")

#     return await expand_about(about)


# # ----------------- UPDATE -----------------

# @router.put("/{about_id}", dependencies=[Depends(verify_user)])
# async def update_about(
#     about_id: str,
#     payload: AboutUpdate,
#     user=Depends(verify_user)
# ):
#     existing = await AboutRepository.get_by_id(about_id)
#     if not existing:
#         raise HTTPException(404, "About page not found")

#     update_data = payload.dict(exclude_unset=True)

#     if "product_images" in update_data:
#         keep = update_data["product_images"].get("keep", [])
#         new = update_data["product_images"].get("new_uploaded_ids", [])
#         update_data["product_images"] = keep + new

#     about = await AboutRepository.update(about_id, update_data)
#     about = await expand_about(about)

#     await NotificationRepository.create_notification({
#         "user_email": user["sub"],
#         "message": f"About page '{about.get('title')}' updated",
#         "type": "about_updated",
#         "created_at": datetime.utcnow()
#     })

#     return {
#         "message": "About page updated",
#         "about": about
#     }


# # ----------------- DELETE -----------------

# @router.delete("/{about_id}", dependencies=[Depends(verify_user)])
# async def delete_about(about_id: str, user=Depends(verify_user)):
#     about = await AboutRepository.get_by_id(about_id)
#     if not about:
#         raise HTTPException(404, "About page not found")

#     await AboutRepository.delete(about_id)

#     await NotificationRepository.create_notification({
#         "user_email": user["sub"],
#         "message": f"About page '{about.get('title')}' deleted",
#         "type": "about_deleted",
#         "created_at": datetime.utcnow()
#     })

#     return {"message": "About page deleted"}
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List

from app.schemas.about_schema import AboutCreate, AboutUpdate
from app.repository.about_repository import AboutRepository
from app.repository.upload_repository import UploadRepository
from app.repository.file_url_repository import FileUrlRepository
from app.repository.notification_repository import NotificationRepository
from app.services.auth_dependency import verify_user
from app.services.cloudinary_service import ensure_accessible_url

router = APIRouter(prefix="/about", tags=["About"])


# =========================================================
# FILE EXPANSION (BASE64 CONTENT)
# =========================================================

async def expand_file(file_id: str):
    if not file_id:
        return None

    f = await UploadRepository.get_file_by_id(file_id)
    if not f:
        return None

    return {
        "id": str(f["_id"]),
        "filename": f["filename"],
        "content": f["content"]
    }


async def expand_files(file_ids: List[str]):
    result = []
    for fid in file_ids or []:
        file = await expand_file(fid)
        if file:
            result.append(file)
    return result

async def expand_video(file_id: str):
    if not file_id:
        return None

    f = await FileUrlRepository.get_url_by_file_id(file_id)
    if not f:
        return None

    return {
        "file_id": str(file_id),
        "filename": f.get("filename"),
        "url": ensure_accessible_url(f.get("url")),
        "type": "video",
    }

async def expand_about(doc: dict):

    doc["about_video_file"] = await expand_video(doc.get("about_video"))

    doc["product_images_files"] = await expand_files(
        doc.get("product_images", [])
    )

    for industry in doc.get("industries_served", []):
        industry["image_file"] = await expand_file(
            industry.get("image_id")
        )

    # ✅ FIXED gallery
    gallery_files = []
    for item in doc.get("gallery", []):
        if isinstance(item, str):
            file = await expand_file(item)
        elif isinstance(item, dict):
            file = await expand_file(item.get("file_id"))
        else:
            file = None

        if file:
            gallery_files.append(file)

    doc["gallery_files"] = gallery_files
    return doc


# =========================================================
# FILE EXPANSION (CLOUDINARY URL)
# =========================================================

async def expand_file_url(file_id: str):
    if not file_id:
        return None

    f = await FileUrlRepository.get_url_by_file_id(file_id)
    if not f:
        return None

    return {
        "file_id": file_id,
        "filename": f["filename"],
        "url": ensure_accessible_url(f["url"])
    }


async def expand_file_url_list(file_ids: List[str]):
    result = []
    for fid in file_ids or []:
        file = await expand_file_url(fid)
        if file:
            result.append(file)
    return result


async def expand_about_url(doc: dict):

    doc["about_video_file"] = await expand_file_url(
        doc.get("about_video")
    )

    doc["product_images_files"] = await expand_file_url_list(
        doc.get("product_images", [])
    )

    for industry in doc.get("industries_served", []):
        industry["image_file"] = await expand_file_url(
            industry.get("image_id")
        )

    # ✅ FIXED gallery
    gallery_files = []
    for item in doc.get("gallery", []):
        if isinstance(item, str):
            file = await expand_file_url(item)
        elif isinstance(item, dict):
            file = await expand_file_url(item.get("file_id"))
        else:
            file = None

        if file:
            gallery_files.append(file)

    doc["gallery_files"] = gallery_files
    return doc


# =========================================================
# CREATE
# =========================================================

@router.post("/", dependencies=[Depends(verify_user)])
async def create_about(payload: AboutCreate, user=Depends(verify_user)):
    about_id = await AboutRepository.create_about(payload.dict())

    about = await AboutRepository.get_by_id(about_id)
    about = await expand_about(about)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"About page '{payload.title}' created",
        "type": "about_created",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "About page created",
        "about_id": about_id,
        "about": about
    }


# =========================================================
# GET ALL (CONTENT)
# =========================================================

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


# =========================================================
# GET ONE (CONTENT)
# =========================================================

@router.get("/{about_id}", dependencies=[Depends(verify_user)])
async def get_about(about_id: str):
    about = await AboutRepository.get_by_id(about_id)
    if not about:
        raise HTTPException(404, "About page not found")

    return await expand_about(about)


# =========================================================
# GET ALL (URL)
# =========================================================

@router.get("/url/")
async def get_about_url():
    data = await AboutRepository.get_all()  # ✅ FIXED

    return {
        "count": len(data),
        "about_pages": [await expand_about_url(d) for d in data]
    }


# =========================================================
# GET ONE (URL)
# =========================================================

@router.get("/url/{about_id}")
async def get_about_url_by_id(about_id: str):
    about = await AboutRepository.get_by_id(about_id)
    if not about:
        raise HTTPException(404, "About page not found")

    return await expand_about_url(about)


# =========================================================
# UPDATE
# =========================================================

@router.put("/{about_id}", dependencies=[Depends(verify_user)])
async def update_about(
    about_id: str,
    payload: AboutUpdate,
    user=Depends(verify_user)
):
    existing = await AboutRepository.get_by_id(about_id)
    if not existing:
        raise HTTPException(404, "About page not found")

    # only update fields actually sent
    update_data = payload.dict(exclude_unset=True)

    # 🚫 REMOVED:
    # - product_images merging
    # - industries_served
    # - object gallery handling

    await AboutRepository.update(about_id, update_data)

    # reload + expand
    about = await AboutRepository.get_by_id(about_id)
    about = await expand_about(about)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"About page '{about.get('title')}' updated",
        "type": "about_updated",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "About page updated",
        "about": about
    }


# =========================================================
# DELETE
# =========================================================

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
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {"message": "About page deleted"}
