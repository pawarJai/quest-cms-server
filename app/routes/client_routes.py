from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Union
from datetime import datetime
from app.repository.file_url_repository import FileUrlRepository
from app.repository.client_repository import ClientRepository
from app.repository.upload_repository import UploadRepository
from app.repository.notification_repository import NotificationRepository
from app.services.auth_dependency import verify_user
from app.schemas.client_schema import ClientCreate, ClientUpdate

router = APIRouter(prefix="/clients", tags=["Clients"])


# helper to expand file ids to {id, filename, content}
async def expand_file_ids(file_ids: List[str]):
    expanded = []
    for fid in file_ids or []:
        file_data = await UploadRepository.get_file_by_id(fid)
        if file_data:
            expanded.append({
                "id": file_data["_id"],
                "filename": file_data["filename"],
                "content": file_data["content"]
            })
    return expanded


# ------------------------------------------------------------------
# Helper: expand file ids to Cloudinary URLs (Client)
# ------------------------------------------------------------------
async def expand_file_url_ids(file_ids: List[str]):
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


async def expand_client_url(client: dict):
    if not client or not client.get("client_logo"):
        return client

    if isinstance(client["client_logo"], list):
        client["client_logo"] = await expand_file_url_ids(client["client_logo"])
    else:
        f = await FileUrlRepository.get_url_by_file_id(client["client_logo"])
        if f:
            client["client_logo"] = {
                "file_id": client["client_logo"],
                "filename": f["filename"],
                "url": f["url"]
            }

    return client




@router.get("/url")
async def get_clients_url():
    clients = await ClientRepository.get_all_clients()

    expanded = []
    for client in clients:
        expanded.append(await expand_client_url(client))

    return {
        "count": len(expanded),
        "clients": expanded
    }


@router.get("/url/{client_id}")
async def get_client_url(client_id: str):
    client = await ClientRepository.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client = await expand_client_url(client)
    return client



@router.post("/", dependencies=[Depends(verify_user)])
async def create_client(payload: ClientCreate, user=Depends(verify_user)):
    client_dict = payload.dict()

    client_id = await ClientRepository.create_client(client_dict)

    # Fetch created client
    client = await ClientRepository.get_client_by_id(client_id)

    # Expand client_logo
    if isinstance(client.get("client_logo"), list):
        client["client_logo"] = await expand_file_ids(client["client_logo"])
    elif client.get("client_logo"):
        file_doc = await UploadRepository.get_file_by_id(client["client_logo"])
        if file_doc:
            client["client_logo"] = {
                "id": file_doc["_id"],
                "filename": file_doc["filename"],
                "content": file_doc["content"]
            }

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"Client '{client_dict.get('client_name')}' has been created.",
        "type": "client_created",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "Client created successfully",
        "client_id": client_id,
        "client": client
    }


async def expand_client(client: dict):
    if not client or not client.get("client_logo"):
        return client

    if isinstance(client["client_logo"], list):
        client["client_logo"] = await expand_file_ids(client["client_logo"])
    else:
        file_doc = await UploadRepository.get_file_by_id(client["client_logo"])
        if file_doc:
            client["client_logo"] = {
                "id": file_doc["_id"],
                "filename": file_doc["filename"],
                "content": file_doc["content"]
            }
    return client


@router.get("/", dependencies=[Depends(verify_user)])
async def get_clients():
    clients = await ClientRepository.get_all_clients()

    expanded = []
    for client in clients:
        expanded.append(await expand_client(client))

    return {
        "count": len(expanded),
        "clients": expanded
    }

@router.get("/{client_id}", dependencies=[Depends(verify_user)])
async def get_client(client_id: str):
    client = await ClientRepository.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client = await expand_client(client)
    return client


@router.delete("/{client_id}", dependencies=[Depends(verify_user)])
async def delete_client(client_id: str, user=Depends(verify_user)):
    client = await ClientRepository.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    await ClientRepository.delete_client(client_id)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"Client '{client.get('client_name')}' has been deleted.",
        "type": "client_deleted",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "Client deleted successfully"
    }


@router.put("/{client_id}", dependencies=[Depends(verify_user)])
async def update_client(
    client_id: str,
    payload: ClientUpdate,
    user=Depends(verify_user)
):
    existing = await ClientRepository.get_client_by_id(client_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = payload.dict(exclude_unset=True)

    # ---- Handle client_logo like Product ----
    if "client_logo" in update_data:
        cl = update_data["client_logo"]

        if isinstance(cl, dict):
            keep = cl.get("keep", [])
            new_uploaded = cl.get("new_uploaded_ids", [])
            update_data["client_logo"] = keep + new_uploaded

        elif isinstance(cl, list):
            update_data["client_logo"] = cl

        elif isinstance(cl, str):
            update_data["client_logo"] = cl

    await ClientRepository.update_client(client_id, update_data)

    client = await ClientRepository.get_client_by_id(client_id)
    client = await expand_client(client)

    await NotificationRepository.create_notification({
        "user_email": user["sub"],
        "message": f"Client '{client.get('client_name')}' has been updated.",
        "type": "client_updated",
        "created_at": datetime.utcnow(),
        "read": False
    })

    return {
        "message": "Client updated successfully",
        "client": client
    }
