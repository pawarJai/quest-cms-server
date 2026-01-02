from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union, List


class GalleryUpdate(BaseModel):
    keep: List[str] = []
    new_uploaded_ids: List[str] = []


class NewsBase(BaseModel):
    title: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None

    news_logo: Optional[str] = None
    cover_image: Optional[str] = None
    created_by: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class NewsCreate(NewsBase):
    news_images: Optional[Union[List[str], GalleryUpdate]] = []


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None

    news_logo: Optional[str] = None
    cover_image: Optional[str] = None
    news_images: Optional[Union[List[str], GalleryUpdate]] = None

    model_config = ConfigDict(populate_by_name=True)


class NewsOut(NewsBase):
    id: str = Field(alias="_id")
    news_images: List[str] = []

    model_config = ConfigDict(populate_by_name=True)
