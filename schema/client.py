from pydantic import BaseModel
from typing import Optional

class ClientBase(BaseModel):
    telephone: Optional[str] = None
    adresse: Optional[str] = None

class ClientCreate(ClientBase):
    id_utilisateur: int

class ClientRead(ClientBase):
    id_utilisateur: int

    class Config:
        from_attributes = True
