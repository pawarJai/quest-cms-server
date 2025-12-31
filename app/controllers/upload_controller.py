from fastapi import APIRouter, UploadFile, File,Depends,HTTPException
from app.repository.upload_repository import UploadRepository
from app.services.auth_dependency import verify_user
from app.repository.file_url_repository import FileUrlRepository
from app.services.cloudinary_service import upload_to_cloudinary

router = APIRouter()


@router.post("/upload/images", dependencies=[Depends(verify_user)])
async def upload_images(files: list[UploadFile] = File(...)):
    saved = []

    for file in files:
        file_bytes = await file.read()

        # 1️⃣ Upload to Cloudinary FIRST
        cloud_url = await upload_to_cloudinary(
            file_bytes,
            file.filename,
            resource_type="image"
        )

        # 2️⃣ Store BASE64 in existing collection
        file_id = await UploadRepository.save_file(
            file.filename,
            file_bytes
        )

        # 3️⃣ Store Cloudinary URL in second collection
        await FileUrlRepository.save_url(
            file_id=file_id,
            filename=file.filename,
            url=cloud_url,
            file_type="image"
        )

        saved.append({
            "id": file_id,
            "filename": file.filename,
            "cloudinary_url": cloud_url
        })

    return saved

@router.post("/upload/docs", dependencies=[Depends(verify_user)])
async def upload_docs(files: list[UploadFile] = File(...)):
    saved = []

    for file in files:
        file_bytes = await file.read()

        cloud_url = await upload_to_cloudinary(
            file_bytes,
            file.filename,
            resource_type="raw"
        )

        file_id = await UploadRepository.save_file(
            file.filename,
            file_bytes
        )

        await FileUrlRepository.save_url(
            file_id,
            file.filename,
            cloud_url,
            "doc"
        )

        saved.append({
            "id": file_id,
            "filename": file.filename,
            "cloudinary_url": cloud_url
        })

    return saved

@router.post("/upload/videos", dependencies=[Depends(verify_user)])
async def upload_videos(files: list[UploadFile] = File(...)):
    saved = []

    for file in files:
        file_bytes = await file.read()

        cloud_url = await upload_to_cloudinary(
            file_bytes,
            file.filename,
            resource_type="video"
        )

        file_id = await UploadRepository.save_file(
            file.filename,
            file_bytes
        )

        await FileUrlRepository.save_url(
            file_id,
            file.filename,
            cloud_url,
            "video"
        )

        saved.append({
            "id": file_id,
            "filename": file.filename,
            "cloudinary_url": cloud_url
        })

    return saved


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