from pydantic import BaseModel, ConfigDict
from typing import Optional

class ClientBase(BaseModel):
    telephone: Optional[str] = None
    adresse: Optional[str] = None

class ClientCreate(ClientBase):
    id_utilisateur: int

class ClientRead(ClientBase):
    id_client: int
    id_utilisateur: int
    actif: bool = True
    model_config = ConfigDict(from_attributes=True)
