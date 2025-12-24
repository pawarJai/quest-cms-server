from pydantic import BaseModel
from typing import List, Optional


class Specification(BaseModel):
    key: str
    value: str
    note: Optional[str] = None


class Feature(BaseModel):
    title: str
    details: str
    image_id: Optional[str] = None


class Product(BaseModel):
    name: str
    productType: Optional[str] = None

    short_description: Optional[str] = None
    long_description: Optional[str] = None

    price: Optional[float] = None

    cover_image: Optional[str] = None
    images: List[str] = []
    product_360_image: Optional[str] = None
    product_3d_video: Optional[str] = None

    documents: List[str] = []

    specifications: List[Specification] = []
    features: List[Feature] = []

    created_by: Optional[str] = None
    created_at: Optional[str] = None
