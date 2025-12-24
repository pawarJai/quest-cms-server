from fastapi import APIRouter, UploadFile, File,Depends,HTTPException
from app.repository.upload_repository import UploadRepository
from app.services.auth_dependency import verify_user

router = APIRouter()


@router.post("/upload/images",dependencies=[Depends(verify_user)])
async def upload_images(files: list[UploadFile] = File(...)):
    saved = []

    for file in files:
        bytes_content = await file.read()
        file_id = await UploadRepository.save_file(file.filename, bytes_content)

        saved.append({
            "id": file_id,
            "filename": file.filename
        })
        

    return saved


@router.post("/upload/docs",dependencies=[Depends(verify_user)])
async def upload_docs(files: list[UploadFile] = File(...)):
    saved = []

    for file in files:
        bytes_content = await file.read()
        file_id = await UploadRepository.save_file(file.filename, bytes_content)

        saved.append({
            "id": file_id,
            "filename": file.filename
        })

    return saved

@router.post("/upload/videos",dependencies=[Depends(verify_user)])
async def upload_docs(files: list[UploadFile] = File(...)):
    saved = []

    for file in files:
        bytes_content = await file.read()
        file_id = await UploadRepository.save_file(file.filename, bytes_content)

        saved.append({
            "id": file_id,
            "filename": file.filename
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