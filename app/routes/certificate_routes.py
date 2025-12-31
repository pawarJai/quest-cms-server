from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from app.repository.file_url_repository import FileUrlRepository
from app.repository.certificate_repository import CertificateRepository
from app.repository.upload_repository import UploadRepository
from app.repository.notification_repository import NotificationRepository
from app.services.auth_dependency import verify_user
from app.schemas.certificate_schema import CertificateCreate, CertificateUpdate
import logging

logger = logging.getLogger("certifications")
logger.setLevel(logging.INFO)
router = APIRouter(prefix="/certifications", tags=["Certifications"])


# ------------------------------------------------------------------
# Helper: expand file ids to {id, filename, content}
# ------------------------------------------------------------------
async def expand_file_ids(file_ids: List[str]):
    expanded = []
    for fid in file_ids or []:
        file_data = await UploadRepository.get_file_by_id(fid)
        if file_data:
            expanded.append({
                "id": str(file_data["_id"]),
                "filename": file_data["filename"],
                "content": file_data["content"]
            })
    return expanded


async def expand_certificate(cert: dict):
    if not cert or not cert.get("certificate_logo"):
        return cert

    if isinstance(cert["certificate_logo"], list):
        cert["certificate_logo"] = await expand_file_ids(cert["certificate_logo"])
    else:
        file_doc = await UploadRepository.get_file_by_id(cert["certificate_logo"])
        if file_doc:
            cert["certificate_logo"] = {
                "id": str(file_doc["_id"]),
                "filename": file_doc["filename"],
                "content": file_doc["content"]
            }
    return cert


# ------------------------------------------------------------------
# CREATE Certificate (Product-style)
# ------------------------------------------------------------------
@router.post("/", dependencies=[Depends(verify_user)])
async def create_certificate(payload: CertificateCreate, user=Depends(verify_user)):
    cert_dict = payload.dict()

    cert_id = await CertificateRepository.create_certificate(cert_dict)

    cert = await CertificateRepository.get_certificate_by_id(cert_id)
    cert = await expand_certificate(cert)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"Certification '{cert_dict.get('certificate_name')}' has been created.",
        "type": "certificate_created",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "Certificate created successfully",
        "certificate_id": cert_id,
        "certificate": cert
    }


# ------------------------------------------------------------------
# Helper: expand file ids to Cloudinary URLs
# ------------------------------------------------------------------
async def expand_file_url_ids(file_ids: List[str]):
    expanded = []
    for fid in file_ids or []:
        f = await FileUrlRepository.get_url_by_file_id(fid)
        if f:
            expanded.append({
                "file_id": str(fid),
                "filename": f["filename"],
                "url": f["url"]
            })
    return expanded


async def expand_certificate_url(cert: dict):
    if not cert or not cert.get("certificate_logo"):
        return cert

    if isinstance(cert["certificate_logo"], list):
        cert["certificate_logo"] = await expand_file_url_ids(cert["certificate_logo"])
        logger.info("EXPANDED CERT LOGO LIST:", cert["certificate_logo"])
    else:
        f = await FileUrlRepository.get_url_by_file_id(cert["certificate_logo"])
        logger.info("EXPANDED CERT LOGO SINGLE FILE:", f)
        if f:
            cert["certificate_logo"] = {
                "file_id": cert["certificate_logo"],
                "filename": f["filename"],
                "url": f["url"]
            }

    return cert


# ------------------------------------------------------------------
# GET all Certificates (Product-style)
# ------------------------------------------------------------------
@router.get("/")
async def get_certificates():
    certs = await CertificateRepository.get_all_certificates()

    expanded = []
    for cert in certs:
        expanded.append(await expand_certificate(cert))

    return {
        "count": len(expanded),
        "certificates": expanded
    }


# ------------------------------------------------------------------
# GET Certificate by ID (Product-style)
# ------------------------------------------------------------------
@router.get("/{cert_id}")
async def get_certificate(cert_id: str):
    cert = await CertificateRepository.get_certificate_by_id(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    cert = await expand_certificate(cert)
    return cert


# ------------------------------------------------------------------
# UPDATE Certificate (Product-style)
# ------------------------------------------------------------------
@router.put("/{cert_id}", dependencies=[Depends(verify_user)])
async def update_certificate(
    cert_id: str,
    payload: CertificateUpdate,
    user=Depends(verify_user)
):
    existing = await CertificateRepository.get_certificate_by_id(cert_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Certificate not found")

    update_data = payload.dict(exclude_unset=True)

    # ---- Handle certificate_logo (keep + new uploads) ----
    if "certificate_logo" in update_data:
        cl = update_data["certificate_logo"]

        if isinstance(cl, dict):
            keep = cl.get("keep", [])
            new_uploaded = cl.get("new_uploaded_ids", [])
            update_data["certificate_logo"] = keep + new_uploaded

        elif isinstance(cl, list):
            update_data["certificate_logo"] = cl

        elif isinstance(cl, str):
            update_data["certificate_logo"] = cl

    await CertificateRepository.update_certificate(cert_id, update_data)

    cert = await CertificateRepository.get_certificate_by_id(cert_id)
    cert = await expand_certificate(cert)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"Certification '{cert.get('certificate_name')}' has been updated.",
        "type": "certificate_updated",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "Certificate updated successfully",
        "certificate": cert
    }


# ------------------------------------------------------------------
# DELETE Certificate (Product-style)
# ------------------------------------------------------------------
@router.delete("/{cert_id}", dependencies=[Depends(verify_user)])
async def delete_certificate(cert_id: str, user=Depends(verify_user)):
    cert = await CertificateRepository.get_certificate_by_id(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    await CertificateRepository.delete_certificate(cert_id)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"Certification '{cert.get('certificate_name')}' has been deleted.",
        "type": "certificate_deleted",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "Certificate deleted successfully"
    }


@router.get("/url/")
async def get_certificates_url():
    certs = await CertificateRepository.get_all_certificates()
    logger.info(f"Fetched {len(certs)} certificates for URL expansion.")

    expanded = []
    for cert in certs:
        expanded.append(await expand_certificate_url(cert))

    return {
        "count": len(expanded),
        "certificates": expanded
    }


@router.get("/url/{cert_id}")
async def get_certificate_url(cert_id: str):
    cert = await CertificateRepository.get_certificate_by_id(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    cert = await expand_certificate_url(cert)
    return cert
