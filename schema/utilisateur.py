from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UtilisateurBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    role: str

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurRead(UtilisateurBase):
    id_utilisateur: int
    date_creation: datetime

    class Config:
        from_attributes = True
