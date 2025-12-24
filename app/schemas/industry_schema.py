from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union, List, Dict

# Define the structure for gallery updates
class GalleryUpdate(BaseModel):
    keep: List[str] = []
    new_uploaded_ids: List[str] = []

class IndustryBase(BaseModel):
    industry_name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    industry_logo: Optional[str] = None
    cover_image: Optional[str] = None
    
    # associations
    client_ids: List[str] = []
    product_ids: List[str] = []
    certification_ids: List[str] = []
    created_by: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

class IndustryCreate(IndustryBase):
    # Overriding to allow the dict structure from frontend
    industry_images: Optional[Union[List[str], GalleryUpdate]] = []

class IndustryUpdate(BaseModel):
    industry_name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    industry_logo: Optional[str] = None
    cover_image: Optional[str] = None
    # Allow either a list or the dictionary structure
    industry_images: Optional[Union[List[str], GalleryUpdate]] = None
    client_ids: Optional[List[str]] = None
    product_ids: Optional[List[str]] = None
    certification_ids: Optional[List[str]] = None

    model_config = ConfigDict(populate_by_name=True)

class IndustryOut(IndustryBase):
    id: str = Field(alias="_id")
    industry_images: List[str] = []
    model_config = ConfigDict(populate_by_name=True)