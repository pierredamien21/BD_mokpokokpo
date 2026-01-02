from pydantic import BaseModel, ConfigDict

class ClientBase(BaseModel):
    telephone: str | None = None
    adresse: str | None = None

class ClientCreate(ClientBase):
    id_utilisateur: int

class ClientOut(ClientBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_client: int
    id_utilisateur: int
