from fastapi import APIRouter, UploadFile, File,Depends,HTTPException, Request
from app.repository.upload_repository import UploadRepository
from app.services.auth_dependency import verify_user
from app.repository.file_url_repository import FileUrlRepository
from app.services.cloudinary_service import upload_to_cloudinary
from uuid import uuid4
import os
import asyncio
import logging
router = APIRouter()


@router.post("/upload/images", dependencies=[Depends(verify_user)])
async def upload_images(request: Request, files: list[UploadFile] = File(...), category: str | None = None):
    async def process_file(file: UploadFile):
        file_bytes = await file.read()
        cloud_task = asyncio.create_task(upload_to_cloudinary(
            file_bytes,
            file.filename,
            resource_type="image",
            key_prefix=category
        ))
        save_task = asyncio.create_task(UploadRepository.save_file(
            file.filename,
            file_bytes
        ))
        cloud_res, save_res = await asyncio.gather(cloud_task, save_task, return_exceptions=True)
        cloud_url = cloud_res if not isinstance(cloud_res, Exception) else ""
        if isinstance(cloud_res, Exception):
            logging.exception(f"Cloud upload exception filename={file.filename} category={category}")
        require_s3 = os.environ.get("AWS_S3_REQUIRED", "").lower() in ("1", "true", "yes")
        if require_s3 and (not cloud_url or (isinstance(cloud_url, str) and cloud_url.startswith("/"))):
            raise HTTPException(status_code=500, detail="S3 upload failed")
        if isinstance(save_res, Exception):
            logging.error(f"UploadRepository.save_file failed: {save_res}")
            file_id = str(uuid4())
        else:
            file_id = save_res
        try:
            await FileUrlRepository.save_url(
                file_id=file_id,
                filename=file.filename,
                url=cloud_url,
                file_type="image"
            )
        except Exception as e:
            logging.error(f"FileUrlRepository.save_url failed: {e}")
        absolute_cloudinary_url = cloud_url if not isinstance(cloud_url, str) or not cloud_url.startswith("/") else (str(request.base_url) + cloud_url.lstrip("/"))
        return {
            "id": file_id,
            "filename": file.filename,
            "cloudinary_url": absolute_cloudinary_url,
            "url": absolute_cloudinary_url
        }
    tasks = [process_file(f) for f in files]
    return await asyncio.gather(*tasks)

@router.post("/upload/docs", dependencies=[Depends(verify_user)])
async def upload_docs(request: Request, files: list[UploadFile] = File(...), category: str | None = None):
    async def process_file(file: UploadFile):
        file_bytes = await file.read()
        cloud_task = asyncio.create_task(upload_to_cloudinary(
            file_bytes,
            file.filename,
            resource_type="raw",
            key_prefix=category
        ))
        save_task = asyncio.create_task(UploadRepository.save_file(
            file.filename,
            file_bytes
        ))
        cloud_res, save_res = await asyncio.gather(cloud_task, save_task, return_exceptions=True)
        cloud_url = cloud_res if not isinstance(cloud_res, Exception) else ""
        if isinstance(cloud_res, Exception):
            logging.exception(f"Cloud upload exception filename={file.filename} category={category}")
        require_s3 = os.environ.get("AWS_S3_REQUIRED", "").lower() in ("1", "true", "yes")
        if require_s3 and (not cloud_url or (isinstance(cloud_url, str) and cloud_url.startswith("/"))):
            raise HTTPException(status_code=500, detail="S3 upload failed")
        if isinstance(save_res, Exception):
            logging.error(f"UploadRepository.save_file failed: {save_res}")
            file_id = str(uuid4())
        else:
            file_id = save_res
        try:
            await FileUrlRepository.save_url(
                file_id,
                file.filename,
                cloud_url,
                "doc"
            )
        except Exception as e:
            logging.error(f"FileUrlRepository.save_url failed: {e}")
        absolute_cloudinary_url = cloud_url if not isinstance(cloud_url, str) or not cloud_url.startswith("/") else (str(request.base_url) + cloud_url.lstrip("/"))
        return {
            "id": file_id,
            "filename": file.filename,
            "cloudinary_url": absolute_cloudinary_url,
            "url": absolute_cloudinary_url
        }
    tasks = [process_file(f) for f in files]
    return await asyncio.gather(*tasks)

@router.post("/upload/videos", dependencies=[Depends(verify_user)])
async def upload_videos(request: Request, files: list[UploadFile] = File(...), category: str | None = None):
    async def process_file(file: UploadFile):
        file_bytes = await file.read()
        cloud_url = await upload_to_cloudinary(
            file_bytes,
            file.filename,
            resource_type="video",
            key_prefix=category
        )
        if not cloud_url:
            logging.error(f"Cloud upload returned empty url filename={file.filename} category={category}")
        require_s3 = os.environ.get("AWS_S3_REQUIRED", "").lower() in ("1", "true", "yes")
        if require_s3 and (not cloud_url or (isinstance(cloud_url, str) and cloud_url.startswith("/"))):
            raise HTTPException(status_code=500, detail="S3 upload failed")
        file_id = str(uuid4())
        try:
            await FileUrlRepository.save_url(
                file_id=file_id,
                filename=file.filename,
                url=cloud_url,
                file_type="video"
            )
        except Exception as e:
            logging.error(f"FileUrlRepository.save_url failed: {e}")
        absolute_cloudinary_url = cloud_url if not isinstance(cloud_url, str) or not cloud_url.startswith("/") else (str(request.base_url) + cloud_url.lstrip("/"))
        return {
            "id": file_id,
            "filename": file.filename,
            "cloudinary_url": absolute_cloudinary_url,
            "url": absolute_cloudinary_url
        }
    tasks = [process_file(f) for f in files]
    data = await asyncio.gather(*tasks)
    return {"success": True, "data": data}

@router.get("/{file_id}")
async def get_file(file_id: str):
    file_doc = await UploadRepository.get_file_by_id(file_id)
    if not file_doc:
        raise HTTPException(404, "File not found")
    # return as JSON with base64 content; frontend can use `data:image/...;base64,${content}`
    return {
        "id": file_doc["_id"],
        "filename": file_doc["filename"],
        "content": file_doc["content"]
    }
