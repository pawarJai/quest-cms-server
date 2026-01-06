from pydantic import BaseModel
from typing import Optional, List

class AboutBase(BaseModel):
    title: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    about_video: Optional[str] = None
    gallery: List[str] = []
    industry_ids: List[str] = []
    product_ids: List[str] = []


class AboutCreate(AboutBase):
    pass


class AboutUpdate(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    about_video: Optional[str] = None
    gallery: Optional[List[str]] = None
    industry_ids: Optional[List[str]] = None
    product_ids: Optional[List[str]] = None

    class Config:
        extra = "forbid"
