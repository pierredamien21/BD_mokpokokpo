from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional
from schema.enums import RoleEnum

class UtilisateurBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    role: RoleEnum

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurRead(UtilisateurBase):
    id_utilisateur: int
    date_creation: datetime
    actif: bool = True
    model_config = ConfigDict(from_attributes=True)



class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
