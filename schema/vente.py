from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class VenteCreate(BaseModel):
    id_commande: int
    chiffre_affaires: Decimal

class VenteRead(VenteCreate):
    id_vente: int
    date_vente: datetime

    class Config:
        from_attributes = True
