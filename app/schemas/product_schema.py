# app/schemas/product_schema.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Union

class Specification(BaseModel):
    key: str
    value: str
    note: Optional[str] = None


class Feature(BaseModel):
    title: str
    details: str
    image_id: Optional[str] = None   # 🔹 feature image


class ProductBase(BaseModel):
    name: str
    productType: Optional[str] = None

    short_description: Optional[str] = None
    long_description: Optional[str] = None

    price: Optional[float] = None

    cover_image: Optional[str] = None        # 🔹 cover image id
    images: List[str] = []                   # gallery images
    product_360_image: Optional[str] = None  # 🔹 360 image
    product_3d_video: Optional[str] = None   # 🔹 3D video

    documents: List[str] = []

    specifications: List[Specification] = []
    features: List[Feature] = []

    created_by: Optional[str] = None          # 🔹 user email


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str]
    productType: Optional[str]

    short_description: Optional[str]
    long_description: Optional[str]
    price: Optional[float]

    cover_image: Optional[str]
    product_360_image: Optional[str]
    product_3d_video: Optional[str]

    images: Optional[Dict[str, List[str]]]
    documents: Optional[Dict[str, List[str]]]

    specifications: Optional[List[Specification]]
    features: Optional[List[Feature]]


class ProductFilterRequest(BaseModel):
    page: int = 1
    limit: int = 10
    productType: Optional[str] = None
    specifications: Optional[Dict[str, str]] = None