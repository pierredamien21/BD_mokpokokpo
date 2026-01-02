from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

class VenteCreate(BaseModel):
    id_commande: int
    chiffre_affaires: Decimal

class VenteOut(VenteCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id_vente: int
    date_vente: datetime