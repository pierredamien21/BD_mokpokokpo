from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UtilisateurBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    role: str

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurOut(UtilisateurBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_utilisateur: int
    date_creation: datetime