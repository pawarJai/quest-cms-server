# from fastapi import APIRouter, HTTPException, Depends
# from app.schemas.product_schema import ProductCreate, ProductUpdate
# from app.repository.product_repository import ProductRepository
# from app.services.auth_dependency import verify_user
# from app.repository.notification_repository import NotificationRepository
# from datetime import datetime
# router = APIRouter(prefix="/products", tags=["Products"])


# # ---------------------------------------------------------
# # EXPAND FILE IDs → FULL FILE DETAILS (id, filename, base64)
# # ---------------------------------------------------------
# async def expand_file_ids(file_ids: list[str]):
#     from app.repository.upload_repository import UploadRepository

#     expanded = []
#     for fid in file_ids:
#         file_data = await UploadRepository.get_file_by_id(fid)
#         if file_data:
#             expanded.append({
#                 "id": file_data["_id"],
#                 "filename": file_data["filename"],
#                 "content": file_data["content"],  # base64 image/pdf
#             })
#     return expanded


# # ------------------------- CREATE PRODUCT -------------------------
# @router.post("/", dependencies=[Depends(verify_user)])
# async def create_product(payload: ProductCreate, user=Depends(verify_user)):
#     product_dict = payload.dict()
#     product_id = await ProductRepository.create_product(product_dict)

#     # Return created product with expanded images & documents
#     product = await ProductRepository.get_product_by_id(product_id)
#     product["images"] = await expand_file_ids(product.get("images", []))
#     product["documents"] = await expand_file_ids(product.get("documents", []))

#     message = f"Product '{product_dict['name']}' has been created."
#     await NotificationRepository.create_notification({
#         "user_email": user["sub"],
#         "message": message,
#         "type": "product_created",
#         "created_at": datetime.utcnow()
#     })

#     return {
#         "message": "Product saved successfully",
#         "product_id": product_id,
#         "product": product
#     }


# # ------------------------- GET ALL PRODUCTS -------------------------
# @router.get("/", dependencies=[Depends(verify_user)])
# async def get_all_products():
#     products = await ProductRepository.get_all_products()

#     expanded_products = []
#     for p in products:
#         p["images"] = await expand_file_ids(p.get("images", []))
#         p["documents"] = await expand_file_ids(p.get("documents", []))
#         expanded_products.append(p)

#     return {"count": len(expanded_products), "products": expanded_products}


# # ------------------------- GET ONE PRODUCT -------------------------
# @router.get("/{product_id}", dependencies=[Depends(verify_user)])
# async def get_product(product_id: str):
#     product = await ProductRepository.get_product_by_id(product_id)
#     if not product:
#         raise HTTPException(404, "Product not found")

#     product["images"] = await expand_file_ids(product.get("images", []))
#     product["documents"] = await expand_file_ids(product.get("documents", []))

#     return product


# # ------------------------- UPDATE PRODUCT -------------------------
# @router.put("/{product_id}", dependencies=[Depends(verify_user)])
# async def update_product(product_id: str, payload: ProductUpdate):
#     existing = await ProductRepository.get_product_by_id(product_id)
#     if not existing:
#         raise HTTPException(404, "Product not found")

#     update_data = {}

#     # ---- Merge images ----
#     if payload.images:
#         keep = payload.images.get("keep", [])
#         new_uploaded = payload.images.get("new_uploaded_ids", [])
#         update_data["images"] = keep + new_uploaded

#     # ---- Merge documents ----
#     if payload.documents:
#         keep_docs = payload.documents.get("keep", [])
#         new_docs = payload.documents.get("new_uploaded_ids", [])
#         update_data["documents"] = keep_docs + new_docs

#     # ---- Merge standard fields ----
#     for field in ["name", "description", "price", "productType", "features", "specifications"]:
#         val = getattr(payload, field)
#         if val is not None:
#             update_data[field] = val

#     await ProductRepository.update_product(product_id, update_data)

#     # Return updated product with expanded images/docs
#     product = await ProductRepository.get_product_by_id(product_id)
#     product["images"] = await expand_file_ids(product.get("images", []))
#     product["documents"] = await expand_file_ids(product.get("documents", []))

#     return {
#         "message": "Product updated successfully",
#         "product": product
#     }


# # ------------------------- DELETE PRODUCT -------------------------
# @router.delete("/{product_id}", dependencies=[Depends(verify_user)])
# async def delete_product(product_id: str, user=Depends(verify_user)):
#     # Fetch product BEFORE deletion
#     product = await ProductRepository.get_product_by_id(product_id)
#     if not product:
#         raise HTTPException(404, "Product not found")

#     # Delete it
#     deleted = await ProductRepository.delete_product(product_id)

#     # Create notification
#     message = f"Product '{product['name']}' has been deleted."
#     await NotificationRepository.create_notification({
#         "user_email": user["sub"],
#         "message": message,
#         "type": "product_deleted",
#         "created_at": datetime.utcnow()
#     })

#     return {"message": "Product deleted successfully"}


from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductFilterRequest,
)
from app.repository.product_repository import ProductRepository
from app.repository.notification_repository import NotificationRepository
from app.repository.file_url_repository import FileUrlRepository
from app.services.auth_dependency import verify_user
from app.repository.upload_repository import UploadRepository
from typing import Optional
import logging
import asyncio
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/products", tags=["Products"])


# ---------------- EXPAND FILE IDS ----------------
async def expand_file(file_id: str):
    if not file_id:
        return None
    f = await UploadRepository.get_file_by_id(file_id)
    if not f:
        return None
    return {"id": f["_id"], "filename": f["filename"], "content": f["content"]}


async def expand_file_list(ids: list[str]):
    return [await expand_file(i) for i in ids if i]


async def expand_file_with_url(file_id: str):
    if not file_id:
        return None
    base = await UploadRepository.get_file_by_id(file_id)
    url_doc = await FileUrlRepository.get_url_by_file_id(file_id)
    if not base and not url_doc:
        return None
    res = {}
    if base:
        res.update(
            {
                "id": base["_id"],
                "filename": base["filename"],
                "content": base["content"],
            }
        )
    else:
        res.update(
            {"id": file_id, "filename": url_doc.get("filename") if url_doc else None}
        )
    if url_doc:
        res.update({"url": url_doc.get("url"), "type": url_doc.get("type")})
    return res


async def expand_file_with_url_list(ids: list[str]):
    return [await expand_file_with_url(i) for i in ids if i]

async def expand_file_meta(file_id: str, request: Request):
    if not file_id:
        return None
    f = await FileUrlRepository.get_url_by_file_id(file_id)
    if not f:
        return {"id": str(file_id), "filename": None, "content": None}
    url_value = f.get("url")
    if isinstance(url_value, str) and url_value.startswith("/"):
        url_value = str(request.base_url) + url_value.lstrip("/")
    return {
        "id": str(file_id),
        "filename": f.get("filename"),
        "url": url_value,
        "content": None,
    }

async def expand_file_meta_list(ids: list[str], request: Request):
    tasks = [expand_file_meta(i, request) for i in ids if i]
    return await asyncio.gather(*tasks) if tasks else []

async def expand_file_url(file_id: str, request: Request):
    if not file_id:
        return None

    f = await FileUrlRepository.get_url_by_file_id(file_id)
    if not f:
        return None

    url_value = f["url"]
    if isinstance(url_value, str) and url_value.startswith("/"):
        url_value = str(request.base_url) + url_value.lstrip("/")
    return {"file_id": str(file_id), "filename": f["filename"], "url": url_value}


async def expand_file_url_list(ids: list[str], request: Request):
    tasks = [expand_file_url(i, request) for i in ids if i]
    return await asyncio.gather(*tasks) if tasks else []


async def expand_video(file_id: str, request: Request):
    if not file_id:
        return None

    f = await FileUrlRepository.get_url_by_file_id(file_id)
    if not f:
        return None

    url_value = f.get("url")
    if isinstance(url_value, str) and url_value.startswith("/"):
        url_value = str(request.base_url) + url_value.lstrip("/")
    return {
        "file_id": str(file_id),
        "filename": f.get("filename"),
        "url": url_value,
        "type": "video",
    }

# ---------------- EXPAND PRODUCT (URL ONLY) ----------------
async def expand_product_url(product: dict, request: Request):
    cover_task = expand_file_url(product.get("cover_image"), request)
    p360_task = expand_file_url(product.get("product_360_image"), request)
    video_task = expand_video(product.get("product_3d_video"), request)
    images_task = expand_file_url_list(product.get("images", []), request)
    docs_task = expand_file_url_list(product.get("documents", []), request)

    features = product.get("features", [])
    feature_tasks = [expand_file_url(f.get("image_id"), request) for f in features]

    cover, p360, video, images, docs, feature_images = await asyncio.gather(
        cover_task, p360_task, video_task, images_task, docs_task, asyncio.gather(*feature_tasks) if feature_tasks else asyncio.gather()
    )

    product["cover_image"] = cover
    product["product_360_image"] = p360
    product["product_3d_video"] = video
    product["images"] = images
    product["documents"] = docs
    for f, img in zip(features, feature_images if feature_images else []):
        f["image"] = img

    return product


def get_pagination(page: int, limit: int):
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    skip = (page - 1) * limit
    return skip, limit


# ---------------- CREATE ----------------
@router.post("/", dependencies=[Depends(verify_user)])
async def create_product(payload: ProductCreate, user=Depends(verify_user)):
    data = payload.dict()
    data["created_by"] = user
    data["created_at"] = datetime.utcnow()

    product_id = await ProductRepository.create_product(data)
    product = await ProductRepository.get_product_by_id(product_id)

    await NotificationRepository.create_notification(
        {
            "user_email": user,
            "message": f"Product '{product['name']}' created",
            "type": "product_created",
            "created_at": datetime.utcnow(),
        }
    )

    return {"message": "Product created", "product": await expand_product(product)}


# ---------------- EXPAND PRODUCT ----------------
async def expand_product(product: dict):
    product["cover_image"] = await expand_file_with_url(product.get("cover_image"))
    product["product_360_image"] = await expand_file_with_url(
        product.get("product_360_image")
    )
    product["product_3d_video"] = await expand_file_with_url(
        product.get("product_3d_video")
    )

    product["images"] = await expand_file_with_url_list(product.get("images", []))
    product["documents"] = await expand_file_with_url_list(product.get("documents", []))

    for f in product.get("features", []):
        f["image"] = await expand_file_with_url(f.get("image_id"))

    return product


# ---------------- GET ALL ----------------
@router.get("/")
async def get_products(page: int = 1, limit: int = 10):
    skip, limit = get_pagination(page, limit)

    products = await ProductRepository.get_products_paginated(skip, limit)
    total = await ProductRepository.count_products()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "products": [await expand_product(p) for p in products],
    }


# ---------------- GET ONE ----------------
@router.get("/{product_id}")
async def get_product(product_id: str):
    product = await ProductRepository.get_product_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return await expand_product(product)


@router.get("/url/")
async def get_products_url(request: Request, page: Optional[int] = None, limit: Optional[int] = None):
    if page is None and limit is None:
        products = await ProductRepository.get_all_products()
        total = len(products)
        expanded = await asyncio.gather(*[expand_product_url(p, request) for p in products]) if products else []
        return {
            "page": 1,
            "limit": total,
            "total": total,
            "products": expanded,
        }
    skip, limit = get_pagination(page or 1, limit or 10)
    products = await ProductRepository.get_products_paginated(skip, limit)
    total = await ProductRepository.count_products()
    expanded = await asyncio.gather(*[expand_product_url(p, request) for p in products]) if products else []
    return {
        "page": page or 1,
        "limit": limit,
        "total": total,
        "products": expanded,
    }


@router.get("/url/{product_id}")
async def get_product_by_id_url(product_id: str, request: Request):
    product = await ProductRepository.get_product_by_id(product_id)

    if not product:
        raise HTTPException(404, "Product not found")

    return await expand_product_url(product, request)


# ---------------- UPDATE ----------------
# @router.put("/{product_id}", dependencies=[Depends(verify_user)])
# async def update_product(product_id: str, payload: ProductUpdate):
#     update_data = payload.dict(exclude_unset=True)

#     if "images" in update_data:
#         imgs = update_data["images"]
#         update_data["images"] = imgs.get("keep", []) + imgs.get("new_uploaded_ids", [])

#     if "documents" in update_data:
#         docs = update_data["documents"]
#         update_data["documents"] = docs.get("keep", []) + docs.get(
#             "new_uploaded_ids", []
#         )

#     await ProductRepository.update_product(product_id, update_data)
#     product = await ProductRepository.get_product_by_id(product_id)
#     return {"message": "Updated", "product": await expand_product(product)}

@router.put("/{product_id}", dependencies=[Depends(verify_user)])
async def update_product(product_id: str, payload: ProductUpdate):
    update_data = payload.dict(exclude_unset=True)

    logging.info("Update product called: %s", update_data)

    product = await ProductRepository.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await ProductRepository.update_product(product_id, update_data)

    updated = await ProductRepository.get_product_by_id(product_id)
    return {
        "message": "Product updated successfully",
        "product": await expand_product(updated)
    }

# ---------------- DELETE ----------------
@router.delete("/{product_id}", dependencies=[Depends(verify_user)])
async def delete_product(product_id: str, request: Request):
    product = await ProductRepository.get_product_by_id(product_id)
    if not product:
        raise HTTPException(404, "Not found")

    await ProductRepository.delete_product(product_id)

    await NotificationRepository.create_notification(
        {
            "user_email": request.state.user,
            "message": f"Product '{product['name']}' deleted",
            "type": "product_deleted",
            "created_at": datetime.utcnow(),
        }
    )

    return {"message": "Deleted"}


@router.post("/filter")
async def filter_products(payload: ProductFilterRequest):
    skip, limit = get_pagination(payload.page, payload.limit)

    query = {}

    # --- productType filter ---
    if payload.productType:
        query["productType"] = payload.productType

    # --- specifications filter ---
    if payload.specifications:
        query["specifications"] = {
            "$all": [
                {"$elemMatch": {"key": k, "value": v}}
                for k, v in payload.specifications.items()
            ]
        }

    # ❗ ABSOLUTE SAFETY
    if not query:
        raise HTTPException(
            status_code=400, detail="At least one valid filter is required"
        )

    products = await ProductRepository.filter_products(query, skip, limit)
    total = await ProductRepository.count_filtered_products(query)

    return {
        "page": payload.page,
        "limit": payload.limit,
        "total": total,
        "products": [await expand_product(p) for p in products],
    }


@router.get("/by-type/{product_type}")
async def get_products_by_type(product_type: str, page: int = 1, limit: int = 10, request: Request = None):
    # pagination
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    skip = (page - 1) * limit

    query = {"productType": product_type}

    products = await ProductRepository.filter_products(query, skip, limit)
    total = await ProductRepository.count_filtered_products(query)

    async def hydrate_meta(p: dict, req: Request):
        cover_task = expand_file_meta(p.get("cover_image"), req)
        p360_task = expand_file_meta(p.get("product_360_image"), req)
        video_task = expand_file_meta(p.get("product_3d_video"), req)
        images_task = expand_file_meta_list(p.get("images", []), req)
        docs_task = expand_file_meta_list(p.get("documents", []), req)
        feature_imgs = [expand_file_meta(f.get("image_id"), req) for f in p.get("features", [])]
        cover, p360, video, images, docs, features_images = await asyncio.gather(
            cover_task,
            p360_task,
            video_task,
            images_task,
            docs_task,
            asyncio.gather(*feature_imgs) if feature_imgs else asyncio.gather()
        )
        p["cover_image"] = cover
        p["product_360_image"] = p360
        # ensure video type key retained
        if video is not None:
            video["type"] = "video"
        p["product_3d_video"] = video
        p["images"] = images
        p["documents"] = docs
        for f, img in zip(p.get("features", []), features_images if features_images else []):
            f["image"] = img
        return p

    expanded = await asyncio.gather(*[hydrate_meta(p, request) for p in products]) if products else []

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "products": expanded,
    }
