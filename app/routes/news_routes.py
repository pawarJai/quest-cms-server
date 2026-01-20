from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
import asyncio
from datetime import datetime

from app.repository.news_repository import NewsRepository
from app.repository.upload_repository import UploadRepository
from app.repository.file_url_repository import FileUrlRepository
from app.repository.notification_repository import NotificationRepository
from app.services.auth_dependency import verify_user
from app.schemas.news_schema import NewsCreate, NewsUpdate

router = APIRouter(prefix="/news", tags=["News"])


# =====================================================
# FILE EXPANSION (CONTENT)
# =====================================================

async def expand_file(file_id: str | None):
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
    expanded = []
    for fid in file_ids or []:
        f = await UploadRepository.get_file_by_id(fid)
        if f:
            expanded.append({
                "id": f["_id"],
                "filename": f["filename"],
                "content": f["content"]
            })
    return expanded


# =====================================================
# FILE EXPANSION (URL)
# =====================================================

async def expand_file_url(file_id: str | None, request: Request):
    if not file_id:
        return None

    f = await FileUrlRepository.get_url_by_file_id(file_id)
    if not f:
        return None

    url_value = f["url"]
    if isinstance(url_value, str) and url_value.startswith("/"):
        url_value = str(request.base_url) + url_value.lstrip("/")

    return {
        "file_id": file_id,
        "filename": f["filename"],
        "url": url_value
    }


async def expand_files_url(file_ids: List[str], request: Request):
    ids = file_ids or []
    docs = await asyncio.gather(
        *[FileUrlRepository.get_url_by_file_id(fid) for fid in ids],
        return_exceptions=False
    )
    result = []
    for fid, f in zip(ids, docs):
        if f:
            url_value = f["url"]
            if isinstance(url_value, str) and url_value.startswith("/"):
                url_value = str(request.base_url) + url_value.lstrip("/")
            result.append({
                "file_id": fid,
                "filename": f["filename"],
                "url": url_value
            })
    return result


# =====================================================
# HYDRATORS
# =====================================================

async def hydrate_news(news: dict):
    if not news:
        return None

    news["news_logo"] = await expand_file(news.get("news_logo"))
    news["cover_image"] = await expand_file(news.get("cover_image"))
    news["news_images"] = await expand_files(news.get("news_images", []))

    return news


async def hydrate_news_url(news: dict, request: Request):
    if not news:
        return None
    logo_task = expand_file_url(news.get("news_logo"), request)
    cover_task = expand_file_url(news.get("cover_image"), request)

    raw_images = news.get("news_images", [])

    image_ids = []
    if isinstance(raw_images, dict):
        image_ids = (
            raw_images.get("keep", []) +
            raw_images.get("new_uploaded_ids", [])
        )
    elif isinstance(raw_images, list):
        image_ids = raw_images

    images_task = expand_files_url(image_ids, request)

    logo, cover, images = await asyncio.gather(logo_task, cover_task, images_task)

    news["news_logo"] = logo
    news["cover_image"] = cover
    news["news_images"] = images
    return news


# =====================================================
# CREATE
# =====================================================

@router.post("/", dependencies=[Depends(verify_user)])
async def create_news(payload: NewsCreate, user=Depends(verify_user)):
    data = payload.dict()
    data["created_by"] = user

    if not data.get("title") or data["title"].strip() == "":
        raise HTTPException(400, "Title cannot be empty")

    news_id = await NewsRepository.create_news(data)
    news = await NewsRepository.get_news_by_id(news_id)

    news = await hydrate_news(news)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"News '{data['title']}' created",
        "type": "news_created",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "News created successfully",
        "news_id": news_id,
        "news": news
    }


# =====================================================
# GET ALL (CONTENT)
# =====================================================

@router.get("/", dependencies=[Depends(verify_user)])
async def get_news():
    news = await NewsRepository.get_all_news()
    return {
        "count": len(news),
        "news": [await hydrate_news(n) for n in news]
    }


# =====================================================
# GET ONE (CONTENT)
# =====================================================

@router.get("/{news_id}", dependencies=[Depends(verify_user)])
async def get_news_by_id(news_id: str):
    news = await NewsRepository.get_news_by_id(news_id)
    if not news:
        raise HTTPException(404, "News not found")

    return await hydrate_news(news)


# =====================================================
# GET ALL (URL)
# =====================================================

@router.get("/url/")
async def get_news_url(request: Request):
    items = await NewsRepository.get_all_news()
    expanded = await asyncio.gather(*[hydrate_news_url(n, request) for n in items]) if items else []
    return {
        "count": len(items),
        "news": expanded
    }


# =====================================================
# GET ONE (URL)
# =====================================================

@router.get("/url/{news_id}")
async def get_news_url_by_id(news_id: str, request: Request):
    news = await NewsRepository.get_news_by_id(news_id)
    if not news:
        raise HTTPException(404, "News not found")

    return await hydrate_news_url(news, request)


# =====================================================
# UPDATE
# =====================================================

@router.put("/{news_id}", dependencies=[Depends(verify_user)])
async def update_news(
    news_id: str,
    payload: NewsUpdate,
    user=Depends(verify_user)
):
    existing = await NewsRepository.get_news_by_id(news_id)
    if not existing:
        raise HTTPException(404, "News not found")

    update_data = payload.dict(exclude_unset=True)

    if isinstance(update_data.get("news_images"), dict):
        keep = update_data["news_images"].get("keep", [])
        new = update_data["news_images"].get("new_uploaded_ids", [])
        update_data["news_images"] = keep + new

    await NewsRepository.update_news(news_id, update_data)

    news = await NewsRepository.get_news_by_id(news_id)
    news = await hydrate_news(news)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"News '{news.get('title')}' updated",
        "type": "news_updated",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "News updated successfully",
        "news": news
    }


# =====================================================
# DELETE
# =====================================================

@router.delete("/{news_id}", dependencies=[Depends(verify_user)])
async def delete_news(news_id: str, user=Depends(verify_user)):
    news = await NewsRepository.get_news_by_id(news_id)
    if not news:
        raise HTTPException(404, "News not found")

    await NewsRepository.delete_news(news_id)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"News '{news.get('title')}' deleted",
        "type": "news_deleted",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {"message": "News deleted successfully"}
