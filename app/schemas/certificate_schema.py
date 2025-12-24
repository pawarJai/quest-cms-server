from pydantic import BaseModel, Field
from typing import Optional
from pydantic import ConfigDict


class CertificateBase(BaseModel):
    certificate_name: str
    certificate_logo: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class CertificateCreate(CertificateBase):
    pass


class CertificateUpdate(BaseModel):
    certificate_name: Optional[str] = None
    certificate_logo: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class CertificateOut(CertificateBase):
    id: str = Field(alias="_id")

    model_config = ConfigDict(populate_by_name=True)
