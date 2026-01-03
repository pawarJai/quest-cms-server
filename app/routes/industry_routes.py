from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime

from app.repository.industry_repository import IndustryRepository
from app.repository.upload_repository import UploadRepository
from app.repository.notification_repository import NotificationRepository
from app.repository.client_repository import ClientRepository
from app.repository.product_repository import ProductRepository
from app.repository.certificate_repository import CertificateRepository
from app.repository.file_url_repository import FileUrlRepository

from app.services.auth_dependency import verify_user
from app.schemas.industry_schema import IndustryCreate, IndustryUpdate

router = APIRouter(prefix="/industries", tags=["Industries"])



# ---------- URL-based expanders ----------

async def expand_clients_url(ids: List[str]):
    result = []
    for cid in ids:
        client = await ClientRepository.get_client_by_id(cid)
        if client:
            from app.routes.client_routes import expand_client_url
            result.append(await expand_client_url(client))
    return result


async def expand_products_url(ids: List[str]):
    result = []
    for pid in ids:
        product = await ProductRepository.get_product_by_id(pid)
        if product:
            from app.routes.product_routes import expand_product_url
            result.append(await expand_product_url(product))
    return result


async def expand_certifications_url(ids: List[str]):
    result = []
    for cid in ids:
        cert = await CertificateRepository.get_certificate_by_id(cid)
        if cert:
            from app.routes.certificate_routes import expand_certificate_url
            result.append(await expand_certificate_url(cert))
    return result



async def expand_file(file_id: str | None):
    if not file_id:
        return None
    file = await UploadRepository.get_file_by_id(file_id)
    if not file:
        return None
    return {
        "id": file["_id"],
        "filename": file["filename"],
        "content": file["content"]
    }


async def expand_files(file_ids: List[str]):
    expanded = []
    for fid in file_ids or []:
        file = await UploadRepository.get_file_by_id(fid)
        if file:
            expanded.append({
                "id": file["_id"],
                "filename": file["filename"],
                "content": file["content"]
            })
    return expanded


# ------------------------------------------------------------------
# URL-based file expanders (Industry)
# ------------------------------------------------------------------
async def expand_file_url(file_id: str | None):
    if not file_id:
        return None

    f = await FileUrlRepository.get_url_by_file_id(file_id)
    if not f:
        return None

    return {
        "file_id": file_id,
        "filename": f["filename"],
        "url": f["url"]
    }


async def expand_files_url(file_ids: List[str]):
    expanded = []
    for fid in file_ids or []:
        f = await FileUrlRepository.get_url_by_file_id(fid)
        if f:
            expanded.append({
                "file_id": fid,
                "filename": f["filename"],
                "url": f["url"]
            })
    return expanded

async def hydrate_industry_url(industry: dict):
    if not industry:
        return None

    industry["industry_logo"] = await expand_file_url(industry.get("industry_logo"))
    industry["cover_image"] = await expand_file_url(industry.get("cover_image"))
    # industry["industry_images"] = await expand_files_url(
    #     industry.get("industry_images", [])
    # )
    raw_images = industry.get("industry_images", [])

    image_ids = []

    if isinstance(raw_images, dict):
        image_ids = (
            raw_images.get("keep", []) +
            raw_images.get("new_uploaded_ids", [])
        )
    elif isinstance(raw_images, list):
        image_ids = raw_images

    # 🔑 normalize ObjectId → str
    image_ids = [str(i) for i in image_ids if i]

    industry["industry_images"] = await expand_files_url(image_ids)

    # ⚠️ Clients / Products / Certifications remain normal objects
    industry["clients"] = await expand_clients_url(industry.get("client_ids", []))
    industry["products"] = await expand_products_url(industry.get("product_ids", []))
    industry["certifications"] = await expand_certifications_url(
        industry.get("certification_ids", [])
    )

    return industry

@router.get("/url/")
async def get_industries_url():
    industries = await IndustryRepository.get_all_industries()

    return {
        "count": len(industries),
        "industries": [await hydrate_industry_url(i) for i in industries]
    }

@router.get("/url/{industry_id}")
async def get_industry_url(industry_id: str):
    industry = await IndustryRepository.get_industry_by_id(industry_id)
    if not industry:
        raise HTTPException(404, "Industry not found")

    return await hydrate_industry_url(industry)


async def expand_clients(ids: List[str]):
    return [c for cid in ids if (c := await ClientRepository.get_client_by_id(cid))]


async def expand_products(ids: List[str]):
    return [p for pid in ids if (p := await ProductRepository.get_product_by_id(pid))]


async def expand_certifications(ids: List[str]):
    return [c for cid in ids if (c := await CertificateRepository.get_certificate_by_id(cid))]


async def hydrate_industry(industry: dict):
    if not industry:
        return None

    industry["industry_logo"] = await expand_file(industry.get("industry_logo"))
    industry["cover_image"] = await expand_file(industry.get("cover_image"))
    industry["industry_images"] = await expand_files(industry.get("industry_images", []))

    industry["clients"] = await expand_clients(industry.get("client_ids", []))
    industry["products"] = await expand_products(industry.get("product_ids", []))
    industry["certifications"] = await expand_certifications(industry.get("certification_ids", []))

    return industry


@router.post("/", dependencies=[Depends(verify_user)])
async def create_industry(payload: IndustryCreate, user=Depends(verify_user)):
    data = payload.dict()
    data["created_by"] = user
  # 1. Cleaner Validation (if not already in IndustryCreate schema)
    if not data.get("industry_name") or data.get("industry_name").strip() == "":
        raise HTTPException(status_code=400, detail="Industry name cannot be empty")

    #

    industry_id = await IndustryRepository.create_industry(data)
    industry = await IndustryRepository.get_industry_by_id(industry_id)

    industry = await hydrate_industry(industry)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"Industry '{data.get('industry_name')}' has been created.",
        "type": "industry_created",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "Industry created successfully",
        "industry_id": industry_id,
        "industry": industry
    }

@router.get("/", dependencies=[Depends(verify_user)])
async def get_industries():
    industries = await IndustryRepository.get_all_industries()
    return {
        "count": len(industries),
        "industries": [await hydrate_industry(i) for i in industries]
    }


@router.get("/{industry_id}", dependencies=[Depends(verify_user)])
async def get_industry(industry_id: str):
    industry = await IndustryRepository.get_industry_by_id(industry_id)
    if not industry:
        raise HTTPException(404, "Industry not found")
    return await hydrate_industry(industry)

@router.put("/{industry_id}", dependencies=[Depends(verify_user)])
async def update_industry(
    industry_id: str,
    payload: IndustryUpdate,
    user=Depends(verify_user)
):
    existing = await IndustryRepository.get_industry_by_id(industry_id)
    if not existing:
        raise HTTPException(404, "Industry not found")

    update_data = payload.dict(exclude_unset=True)

    if isinstance(update_data.get("industry_images"), dict):
        keep = update_data["industry_images"].get("keep", [])
        new = update_data["industry_images"].get("new_uploaded_ids", [])
        update_data["industry_images"] = keep + new

    await IndustryRepository.update_industry(industry_id, update_data)

    industry = await IndustryRepository.get_industry_by_id(industry_id)
    industry = await hydrate_industry(industry)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"Industry '{industry.get('industry_name')}' has been updated.",
        "type": "industry_updated",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "Industry updated successfully",
        "industry": industry
    }

@router.post("/{industry_id}/associate-products", dependencies=[Depends(verify_user)])
async def associate_products(industry_id: str, product_ids: List[str]):
    industry = await IndustryRepository.get_industry_by_id(industry_id)
    if not industry:
        raise HTTPException(404, "Industry not found")

    updated = list(set(industry.get("product_ids", []) + product_ids))

    await IndustryRepository.update_industry(industry_id, {"product_ids": updated})

    return {
        "message": "Products associated successfully",
        "product_ids": updated
    }


@router.delete("/{industry_id}", dependencies=[Depends(verify_user)])
async def delete_industry(industry_id: str, user=Depends(verify_user)):
    industry = await IndustryRepository.get_industry_by_id(industry_id)
    if not industry:
        raise HTTPException(404, "Industry not found")

    await IndustryRepository.delete_industry(industry_id)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"Industry '{industry.get('industry_name')}' has been deleted.",
        "type": "industry_deleted",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {"message": "Industry deleted successfully"}

