from pydantic import BaseModel, Field
from typing import Optional
from pydantic import ConfigDict


class ClientBase(BaseModel):
    client_name: str
    website: Optional[str] = None
    client_logo: Optional[str] = None   # file_id

    model_config = ConfigDict(populate_by_name=True)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    client_name: Optional[str] = None
    website: Optional[str] = None
    client_logo: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class ClientOut(ClientBase):
    id: str = Field(alias="_id")

    model_config = ConfigDict(populate_by_name=True)
