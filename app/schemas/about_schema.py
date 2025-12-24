from pydantic import BaseModel
from typing import List, Optional


class MediaItem(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file_id: str


class IndustryServed(BaseModel):
    title: str
    description: Optional[str] = None
    image_id: str


class AboutBase(BaseModel):
    title: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None

    about_video: Optional[str] = None          # file id
    product_images: List[str] = []              # file ids

    industries_served: List[IndustryServed] = []
    gallery: List[MediaItem] = []


class AboutCreate(AboutBase):
    pass


class AboutUpdate(BaseModel):
    title: Optional[str]
    short_description: Optional[str]
    long_description: Optional[str]

    about_video: Optional[str]
    product_images: Optional[dict]     # { keep, new_uploaded_ids }

    industries_served: Optional[List[IndustryServed]]
    gallery: Optional[List[MediaItem]]
